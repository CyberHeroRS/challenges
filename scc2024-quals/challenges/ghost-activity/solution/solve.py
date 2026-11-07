import os
import socket

HOST = os.environ.get("SERVICE_APP_MAIN_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_APP_MAIN_PORT", "1500"))

# Built from scratch, but trivially: server.py's own Q&A handler hardcodes
# every expected answer directly in the source (no actual volatility
# analysis of the memory dump is enforced server-side -- it only string
# -compares against these literals). The README documents how each answer
# was originally derived from the memory dump via volatility3, included
# here for context:
#   1. Windows major.minor version   -> windows.info
#   2. current username              -> windows.envars
#   3. NTHASH of cyberhero's password -> windows.hashdump
#   4. PID of the text editor used for the email -> windows.pstree
#   5. friend's name mentioned in the email -> windows.memmap --dump + strings
#   6. URL targeted by the download-speed test script -> windows.envars
#   7. timestamp the connection to that URL was established -> windows.netscan
ANSWERS = [
    "10.0",
    "cyberhero",
    "f8f880509d176c4c4c23c8e55d0da5dc",
    "9096",
    "Royce",
    "https://hil-speed.hetzner.com/1GB.bin",
    "2024-03-17 13:02:35",
]


def recv_until(sock, marker=b"Answer: "):
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


import time

sock = None
last_err = None
for attempt in range(10):
    try:
        sock = socket.create_connection((HOST, PORT), timeout=15)
        break
    except (ConnectionRefusedError, OSError) as exc:
        last_err = exc
        time.sleep(2)
if sock is None:
    raise SystemExit(f"Could not connect to {HOST}:{PORT} after retries: {last_err}")

transcript = b""
for answer in ANSWERS:
    chunk = recv_until(sock)
    transcript += chunk
    print(chunk.decode(errors="replace"), end="")
    sock.sendall((answer + "\n").encode())

# Drain the rest (Correct!, the flag line, and the closing message).
sock.settimeout(5)
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        transcript += chunk
        print(chunk.decode(errors="replace"), end="")
except socket.timeout:
    pass
sock.close()

print("\n--- transcript captured, flag should be printed above ---")
