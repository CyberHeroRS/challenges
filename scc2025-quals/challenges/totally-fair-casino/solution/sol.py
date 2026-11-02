import os
import random
import re
import struct

from pwn import *

# ----------------------------------------------------------------------------
# Vulnerability: the server "commits" to a 16-byte ServerSeed by publishing
# sha1(ServerSeed) *before* the bet, and later derives the RNG seed for the
# horse race as sha1(ServerSeed + ClientSeed) where ClientSeed is a fully
# attacker-controlled hex blob of arbitrary bytes. Because the commitment is
# a bare SHA1 digest (no HMAC / keying), knowing H = sha1(ServerSeed) and the
# fixed length of ServerSeed (16 bytes, from Crypto.Random.get_random_bytes)
# is enough to perform a classic length-extension attack: we can compute
# sha1(ServerSeed || glue_padding || suffix) for any suffix we like without
# ever knowing ServerSeed itself. Sending ClientSeed = glue_padding (+
# suffix) makes the server compute exactly that forged digest as the race
# seed. Since Python's `random.Random(seed_bytes)` is a pure deterministic
# function of the seed bytes, we can replicate the server's horse-race logic
# locally to *predict* the winner for our forged seed, then simply bet on
# that horse: a guaranteed win, every round, with zero knowledge of the
# actual secret ServerSeed.
# ----------------------------------------------------------------------------


def _rol(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def sha1_pad(msglen):
    """Standard SHA1 padding (Merkle-Damgard glue) for a message of length msglen bytes."""
    pad = b"\x80"
    pad += b"\x00" * ((55 - msglen) % 64)
    pad += struct.pack(">Q", msglen * 8)
    return pad


def sha1_compress(state, block):
    """One SHA1 compression round, starting from an arbitrary 5-word state."""
    w = list(struct.unpack(">16I", block))
    for i in range(16, 80):
        w.append(_rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1))
    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f = (b & c) | ((~b & 0xFFFFFFFF) & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (_rol(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
        e, d, c, b, a = d, c, _rol(b, 30), a, temp
    return (
        (state[0] + a) & 0xFFFFFFFF,
        (state[1] + b) & 0xFFFFFFFF,
        (state[2] + c) & 0xFFFFFFFF,
        (state[3] + d) & 0xFFFFFFFF,
        (state[4] + e) & 0xFFFFFFFF,
    )


def sha1_extend(orig_hash_hex, orig_len, suffix):
    """Given H = sha1(secret) and len(secret), compute sha1(secret || glue || suffix)
    without knowing secret. Returns (forged_digest, glue_padding)."""
    state = struct.unpack(">5I", bytes.fromhex(orig_hash_hex))
    glue = sha1_pad(orig_len)
    new_len = orig_len + len(glue)
    data = suffix + sha1_pad(new_len + len(suffix))
    for i in range(0, len(data), 64):
        state = sha1_compress(state, data[i : i + 64])
    return struct.pack(">5I", *state), glue


SERVER_SEED_LEN = 16  # rand.get_random_bytes(16) in server.py
SUFFIX = b""  # no suffix needed, the glue padding alone is enough


def predict_winner(server_hash_hex):
    """Forge the race seed from the leaked commitment hash and replicate the
    server's horse-race logic locally to find out which horse wins."""
    forged_digest, glue = sha1_extend(server_hash_hex, SERVER_SEED_LEN, SUFFIX)
    client_seed_hex = (glue + SUFFIX).hex()

    rng = random.Random(forged_digest)
    horses = [1, 1, 1, 1]
    while 14 not in horses:
        h = rng.randint(0, 3)
        horses[h] += 1
    winner = horses.index(14)
    return winner, client_seed_hex


HASH_RE = re.compile(rb"Currently: ([0-9a-f]{40})")
NEW_HASH_RE = re.compile(rb"New PF Hash is: ([0-9a-f]{40})")

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

p = remote(HOST, PORT)

# Go into the "Provably Fair" menu to leak the current commitment hash.
p.sendlineafter(b":? ", b"4")
blob = p.recvuntil(b":? ")
match = HASH_RE.search(blob)
assert match, f"could not find server seed hash commitment in: {blob!r}"
current_hash = match.group(1).decode()
log.info(f"leaked commitment hash: {current_hash}")

# Set our ClientSeed once: it only depends on the (fixed, known) length of
# ServerSeed, not on its secret content, so it never needs to change again.
_, client_seed_hex = predict_winner(current_hash)
p.sendline(b"1")  # the ":? " PF submenu prompt was already consumed above
p.sendlineafter(b"Enter ClientSeed (hexencoded): ", client_seed_hex.encode())
p.sendlineafter(b"Press enter to continue", b"")

ROUNDS = 16  # balance starts at 1, doubles per win; 2**16 == 65536 price of the flag
for i in range(ROUNDS):
    winner, _ = predict_winner(current_hash)
    log.info(f"round {i}: predicted winner horse {winner + 1}")

    p.sendlineafter(b":? ", b"1")
    p.sendlineafter(b"[1-4] ", str(winner + 1).encode())

    result = p.recvuntil(b"Press enter to continue")
    assert b"You win" in result, f"forged bet did not win, round {i}: {result!r}"

    match = NEW_HASH_RE.search(result)
    assert match, f"could not find new server seed hash in: {result!r}"
    current_hash = match.group(1).decode()

    p.sendline(b"")

# Balance is now >= 65536.00$: buy the flag from the shop.
p.sendlineafter(b":? ", b"5")
p.recvuntil(b"4. | Skidd Pass")
p.sendline(b"1")

out = p.recvuntil(b"Press enter to continue", timeout=10)
print(out.decode(errors="replace"))
