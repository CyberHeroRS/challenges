#!/usr/bin/env python3
"""Solver for riscy-encryptor.

The shipped `riscy-encryptor.out` is a statically linked RISC-V binary that
only *encrypts*: it reads `flag.txt`, XORs it against a keystream derived
from a random 4-byte seed (read via getrandom(2)), and writes the 64-byte
result to `enc.bin`. There is no decrypt path in the binary (confirmed by
running it under `qemu-riscv64 -strace`: with no `flag.txt` present it
dies trying to read one, and it never reads `enc.bin` back in).

Crucially, running it repeatedly on the same plaintext under qemu shows the
keystream has period 4 (it cycles every 4 bytes). The flag is 48 bytes,
`enc.bin` is 64 bytes, so the last 16 bytes are zero-padding XORed with the
keystream alone -- which leaks the full 4-byte keystream directly, since
0x00 ^ key == key. Repeating that leaked 4-byte pattern across the whole
64-byte buffer and XORing it back against the real `enc.bin` recovers the
original plaintext (the flag), independent of whatever random seed the
original run used.
"""

from pathlib import Path

enc_path = Path("enc.bin")
enc = enc_path.read_bytes()

keystream_period = enc[-4:]
keystream = (keystream_period * (len(enc) // 4 + 1))[: len(enc)]

plaintext = bytes(c ^ k for c, k in zip(enc, keystream))
flag = plaintext.rstrip(b"\x00").decode()

print(flag)
