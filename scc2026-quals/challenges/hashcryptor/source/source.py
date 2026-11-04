from hashlib import sha256
from os import urandom

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes([i ^ j for i, j in zip(a, b)])

iv = urandom(32)
left_pad = urandom(63)

data = open("prica.md", "rb").read()
encrypted = b""

x = iv
encrypted = iv
for byte in data:
    x = xor_bytes(x, sha256(left_pad + bytes([byte])).digest())
    encrypted += x

open("enkriptovana_prica.enc", "wb").write(encrypted)