"""Solver for Hexor.

Vulnerability: the author builds a "one-time pad" keystream as the
hex-digest of SHA-512(random_bytes), i.e. `sha512(...).hexdigest().encode()`.
A hex digest is composed only of the 16 ASCII characters '0'-'9' and
'a'-'f', so instead of a uniformly random byte (256 possibilities) every
keystream byte can only take one of 16 possible values. On top of that,
the script writes 32 independent encryptions of the *same* flag to
out.txt (a classic many-time-pad setup).

For a given byte position, each of the 32 ciphertext bytes c_j equals
flag_byte XOR k_j, where k_j is guaranteed to be one of the 16 hex
characters. We can therefore brute force, for every candidate flag byte
f in 0..256, whether c_j XOR f is a valid hex character for *all* 32
blocks simultaneously. Only the real flag byte satisfies this for every
block; a wrong guess has only a (16/256)^32 chance of surviving, which
is effectively zero, so the candidate set collapses to a single value.
"""

import string

NUM_BLOCKS = 32
HEX_CHARS = frozenset(string.hexdigits[:16].lower().encode())  # b'0123456789abcdef'


def recover_flag(data: bytes, num_blocks: int) -> bytes:
    block_len = len(data) // num_blocks
    blocks = [data[i * block_len:(i + 1) * block_len] for i in range(num_blocks)]

    flag = bytearray(block_len)
    for pos in range(block_len):
        candidates = set(range(256))
        for block in blocks:
            c = block[pos]
            candidates &= {f for f in candidates if (c ^ f) in HEX_CHARS}
        if len(candidates) != 1:
            raise ValueError(f"byte {pos}: expected a unique candidate, got {candidates}")
        flag[pos] = next(iter(candidates))
    return bytes(flag)


def main() -> None:
    with open("out.txt", "rb") as f:
        data = f.read()

    flag = recover_flag(data, NUM_BLOCKS).decode()
    print(flag)


if __name__ == "__main__":
    main()
