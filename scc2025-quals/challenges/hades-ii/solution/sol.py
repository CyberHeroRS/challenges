import os
import re

from pwn import *
from Crypto.Cipher import AES

context.log_level = "info"

host = os.environ["SERVICE_APP_MAIN_HOST"]
port = int(os.environ["SERVICE_APP_MAIN_PORT"])

p = remote(host, port)

# The oracle requires a 32-byte message. We reuse it as an AES-256 key below,
# so any fixed 32 bytes work (AES-256 accepts any 32-byte key).
msg = b"A" * 32
msg_hex = msg.hex().encode()
cipher = AES.new(msg, AES.MODE_ECB)


def is_pseudorandom(resp: bytes) -> bool:
    # pseudorandom() returns enc(random)||dec(random) under key=msg.
    # Decrypting the first half and encrypting the second half both
    # recover "random" again, so they match for the AES ("fake") oracle,
    # but not for the true_random (XOR) oracle.
    dec_first = cipher.decrypt(resp[:16])
    enc_second = cipher.encrypt(resp[16:])
    return dec_first == enc_second


for i in range(50):
    p.sendlineafter(b"> ", b"3")
    p.sendlineafter(b"State your question for the souls: ", msg_hex)

    p.recvuntil(b"The left soul screams: ")
    left_hex = re.sub(rb"[^0-9a-fA-F]", b"", p.recvline())
    p.recvuntil(b"The right soul screams: ")
    right_hex = re.sub(rb"[^0-9a-fA-F]", b"", p.recvline())

    left_resp = bytes.fromhex(left_hex.decode())
    right_resp = bytes.fromhex(right_hex.decode())

    left_fake = is_pseudorandom(left_resp)
    right_fake = is_pseudorandom(right_resp)

    # The "fake" (pseudorandom) side is NOT the true-random oracle, so we
    # must pick the *other* door, which is the real true_random soul.
    if left_fake and not right_fake:
        door = b"2"
    elif right_fake and not left_fake:
        door = b"1"
    else:
        # Should not happen with real crypto, but fail loudly if it does.
        log.error("Could not distinguish souls on round %d", i)

    p.sendlineafter(b"> ", door)

out = p.recvall(timeout=10)
print(out.decode(errors="replace"))
