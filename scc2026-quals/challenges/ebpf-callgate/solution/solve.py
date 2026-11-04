import base64
import os
import re
import socket
import time

HOST = os.environ.get("SERVICE_EBPF_CALLGATE_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_EBPF_CALLGATE_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/solve.c (author-provided, unchanged
# other than being driven remotely instead of compiled locally).
#
# The service gives a plain shell (bash --login as user "ctf") over netcat --
# there is no exploit to write, since gcc/libc-dev are installed in the
# container itself. The flag is split into 2-byte steps, each stored inside
# BPF maps that a kernel-side eBPF program (attached via a custom syscall
# number, CALLGATE_NR = 0x1337) only advances a "state" counter for once the
# exact right 2-byte pair is replayed for that step (plus every previously
# solved step beforehand, as a running proof-of-knowledge chain). solve.c
# brute-forces each step's two printable bytes by checking whether the
# pinned state_map counter increments after calling the custom syscall --
# a classic oracle search, just gated behind a kernel-side eBPF program
# instead of a userspace one.
#
# We upload solve.c base64-encoded over the shell, compile it with the
# container's own gcc, run it, and scan the raw output for the flag line.

with open(os.path.join(os.path.dirname(__file__), "solve.c"), "rb") as f:
    SOLVE_C_B64 = base64.b64encode(f.read()).decode()


def recv_until_quiet(sock, quiet_for=2.0, overall_timeout=120.0):
    sock.settimeout(quiet_for)
    data = b""
    deadline = time.time() + overall_timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
    return data


s = socket.create_connection((HOST, PORT), timeout=15)

s.sendall(
    f"echo {SOLVE_C_B64} | base64 -d > solve.c && "
    f"gcc -O2 -o solve solve.c && echo COMPILED_OK\n".encode()
)
build_out = recv_until_quiet(s, quiet_for=3.0, overall_timeout=60.0)
print(build_out.decode(errors="replace"))
if b"COMPILED_OK" not in build_out:
    s.close()
    raise SystemExit("solve.c failed to compile in the target container")

s.sendall(b"echo MARKER_START; ./solve; echo MARKER_END\n")
run_out = recv_until_quiet(s, quiet_for=3.0, overall_timeout=90.0)
s.close()

text = run_out.decode(errors="replace")
print(text)

m = re.search(r"FLAG:\s*(\S+)", text)
flag = m.group(1) if m else ""

flag_env = os.environ.get("flag_flag")
if not flag or (flag_env and flag_env not in flag):
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")
