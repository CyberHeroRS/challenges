import os
from Crypto.Hash import CMAC
from Crypto.Cipher import DES3
from Crypto.Util.number import isPrime
from pwn import context, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_RTFM_CDEF0123_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_RTFM_CDEF0123_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/solution.py (author-provided).
#
# RTFM: the "firmware signing" scheme verifies code uploads with a
# textbook-RSA signature over a CMAC-DES3 digest, using a well-known,
# publicly-documented NIST test-vector key (the comment links straight to
# the NIST CMAC spec's example key) instead of a real secret. Worse, the
# server lets *us* supply our own RSA public key (N) alongside the code,
# trusting only that N itself is CMAC-tagged with the same known key
# (that CMAC tag of the firmware's embedded public key, TAG, is also
# public/fixed). Since DES3-CMAC is a CBC-MAC construction over a known
# key, forge_cmac() performs a textbook CBC-MAC forgery: given one valid
# (message, tag) pair (the real firmware's public key + its TAG), it
# constructs an entirely different 128-byte "public key" N whose CMAC
# equals that same TAG, by solving backward through the last CBC-MAC
# block. We brute-force a small odd "offset" parameter until the forged N
# happens to be prime (so we control d = e^-1 mod (N-1) and can sign
# arbitrary code ourselves), then sign `print(FLAG)` with our own forged
# keypair and upload it -- the server accepts it since the CMAC-over-N
# check only ever verifies against the fixed, publicly-known TAG.

KEY = bytes.fromhex(os.environ.get('KEY', '0123456789ABCDEF23456789ABCDEF01456789ABCDEF0123'))

with open(os.path.join(os.path.dirname(__file__), 'signed_firmware.bin'), 'rb') as f:
    fw = f.read()

public_key = fw[128:256]
TAG = CMAC.new(KEY, ciphermod=DES3).update(public_key).digest()

def sign(message, d, n):
    # 0x00 || 0x01 || PS || 0x00 || T
    prefix = b'\0\1' + b'\xff' * (128-3-8) + b'\0'
    x = int.from_bytes(prefix + CMAC.new(KEY, ciphermod=DES3).update(message).digest())
    return pow(x, d, n).to_bytes(128)

def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))

# def cmac(k, m):
#     assert len(m) % 8 == 0
#     chip_k = DES3.new(key = k, mode=DES3.MODE_ECB)
#     l = int.from_bytes(chip_k.encrypt(bytes(8)))
#     r_b = 0b11011
#     k_1 = l << 1
#     if (l & (1<<63)): k_1 ^= r_b
#     k_1 = k_1.to_bytes(8)
#     m_ = [m[i:i + 8] for i in range(0, len(m), 8)]
#     m_[-1] = xor(k_1, m_[-1])
#     c_i = bytes(8)
#     for m_i in m_: c_i = chip_k.encrypt(xor(c_i, m_i))
#     return c_i

def forge_cmac(k, t, offset):
    assert offset & 1
    chip_k = DES3.new(key = k, mode=DES3.MODE_ECB)
    l = int.from_bytes(chip_k.encrypt(bytes(8)))
    r_b = 0b11011
    k_1 = l << 1
    if (l & (1<<63)): k_1 ^= r_b
    k_1 = k_1.to_bytes(8)
    m_ = [bytes(8) for _i in range(128//8)]
    m_[0] = (1<<63).to_bytes(8)
    c_i = bytes(8)
    for m_i in m_[:-2]: c_i = chip_k.encrypt(xor(c_i, m_i))
    m_[-1] = (offset).to_bytes(8)
    m_[-2] = xor(chip_k.decrypt(xor(xor(chip_k.decrypt(t), k_1), m_[-1])), c_i)
    m = b''.join(m_)
    assert CMAC.new(k, ciphermod=DES3).update(m).digest() == t
    return m

for offset in range(1, 5000, 2):
    modified_n = forge_cmac(KEY, TAG, offset)
    if isPrime(int.from_bytes(modified_n)):
        break
print(f'offset = {offset}')

code = b'print(FLAG)'
forged_input = sign(code, pow(65537, -1, int.from_bytes(modified_n)-1), int.from_bytes(modified_n)) + modified_n + code
print(f'forged input: {forged_input.hex()}')
with remote(HOST, PORT) as conn:
    conn.recvuntil(b'uploading new firmware...\n')
    conn.sendline(forged_input.hex().encode())
    output = conn.recvline(timeout=15).decode()
    print(output)

flag_env = os.environ.get('flag_flag')
if flag_env and flag_env not in output:
    raise SystemExit(f'flag mismatch: expected {flag_env!r} to be in {output!r}')