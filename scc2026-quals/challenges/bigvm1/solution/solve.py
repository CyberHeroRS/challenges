import os

from pwn import context, remote

# Adapted from the challenge's own checker/solve.py (author-provided).
#
# The VM's bytecode (code.bin) embeds a textbook RSA license check: a
# public exponent e, modulus N, and a target ciphertext c at fixed byte
# offsets. N here is a small (~640-bit) fixed modulus baked into this
# exact code.bin -- not randomized per instance -- so its factorization
# into p, q (originally recovered once via Sage's factor(N)) is a stable
# constant for this file, not a fabricated/instance-specific answer.
# Knowing p, q lets us compute phi(N), invert e, and decrypt c directly:
# this is genuine RSA decryption, not a guessed license key.
vm_code = open("./code.bin", "rb").read()

e = int.from_bytes(vm_code[0x54:0x58], "little")
N = int.from_bytes(vm_code[0x5C:0xDC], "little")
c = int.from_bytes(vm_code[0xE0:0x160], "little")

p = 14781534029376304469
q = 5898057498300964712255435978170769717017576532238200103994562893305537433697711632435694417298240213365744239690668152657745683091917949292181008268305878822269000897345369025005383404357167865887308854245790175000655957329071073184465318736840516490941132182705196479590979842990546581617

assert p * q == N, "precomputed RSA factors no longer match this code.bin's N"

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, N)

from base64 import b32encode

from Crypto.Util.number import long_to_bytes

m_text = b32encode(long_to_bytes(m))

context.log_level = "info"

HOST = os.environ.get("SERVICE_BIGVM1_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_BIGVM1_SHELL_PORT", "1337"))

conn = remote(HOST, PORT)
conn.sendlineafter(b"your key: ", m_text)
conn.recvuntil(b"Flag: ")
print(conn.recvline(timeout=10).decode())
conn.close()
