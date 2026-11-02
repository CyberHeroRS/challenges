"""
Solver for "Live Laugh Love" (Poly2585 hash family).

Attack, exactly as documented in the challenge README:

1. The service derives per-session keys as `key = x + part`, where `x` is a
   secret 16-byte prefix shared across both keys it builds, and `part` is an
   attacker-supplied 8-byte suffix. The Poly2585 "r" value is just `x`
   (`key[:16]`), so it is identical for every key built from the same `x`.
   The "s" value is `DES3(key[8:]).encrypt(r)`. DES/3DES ignores the low
   (parity) bit of every key byte, so if we submit two suffixes that differ
   only in those parity bits, the two sessions use an *effectively identical*
   3DES key and therefore produce the exact same `s` -- even though `r` was
   already guaranteed equal via the shared `x`. This lets us collide `(r, s)`
   between a hash of the (unknown) flag and hashes of messages we choose.
2. With `(r, s)` pinned down (recovered from two single-byte messages whose
   hashes we observe), we solve for the flag bytes with the lattice
   construction given in the README: the Poly2585 accumulator is linear in
   the message bytes modulo `2^258 - 5`, so the (small) flag bytes and the
   (bounded) reduction quotient together form an unusually short vector that
   LLL recovers.
3. The final hash output is further reduced modulo `2^256`, so a small
   brute-force over the quotient of that reduction (0..3, since
   `2^258 - 5 < 4 * 2^256`) is required for every observed hash value, as the
   README notes.
"""

import os
import re
import socket

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

N = 2 ** 258 - 5
REDUCTION = 2 ** 256


def recv_all(sock, timeout=10):
    sock.settimeout(timeout)
    chunks = []
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    except socket.timeout:
        pass
    return b"".join(chunks)


def collect_hashes():
    # Suffixes differ only in the low (DES parity) bit of every byte, so the
    # two sessions share both `r` (via the common `x` prefix) and `s` (since
    # DES3 ignores parity bits), colliding the Poly2585 (r, s) pair.
    part1 = bytes([0x00] * 8)
    part2 = bytes(b ^ 1 for b in part1)
    m1 = bytes([1])
    m2 = bytes([2])

    payload = (
        part1.hex() + "\n" + part2.hex() + "\n" + m1.hex() + "\n" + m2.hex() + "\n"
    ).encode()

    with socket.create_connection((HOST, PORT), timeout=15) as sock:
        sock.sendall(payload)
        text = recv_all(sock).decode(errors="replace")

    print(text)
    hashes = re.findall(r"h = '(0x[0-9a-f]+)'", text)
    if len(hashes) != 3:
        raise RuntimeError(f"unexpected service output, could not find 3 hashes: {text!r}")
    return [int(h, 16) for h in hashes]


def recover_r_s(h1, h2):
    # h1, h2 were both hashed under the colliding (r, s) pair, with single
    # byte messages [1] and [2]: H = r*m + s (mod N), before the final
    # reduction mod 2^256. Brute force the small quotient of that reduction
    # for each (bounded by 4 since N < 4 * 2^256), then solve the resulting
    # linear system. The genuine (r, s) are both 128-bit (they are `x` and a
    # DES3-ECB output of a 16-byte block), which uniquely identifies the
    # correct quotient guess among the 16 combinations tried.
    candidates = []
    for k1 in range(4):
        H1 = h1 + k1 * REDUCTION
        for k2 in range(4):
            H2 = h2 + k2 * REDUCTION
            r = ((H2 - H1) * pow(2 - 1, -1, N)) % N
            s = (H1 - r) % N
            if r < 2 ** 128 and s < 2 ** 128:
                candidates.append((r, s))
    if not candidates:
        raise RuntimeError("failed to recover (r, s); parity-bit collision did not line up")
    return candidates[0]


def recover_flag(h0, r, s):
    FF = Zmod(N)
    for k0 in range(4):
        H0 = h0 + k0 * REDUCTION
        if H0 >= N:
            continue

        # Lattice construction taken directly from the README.
        m = [[0 for _ in range(18)] for _ in range(18)]
        m[0][0] = -int(FF(H0) - s)

        m[1][0] = N
        m[1][1] = 1

        for i in range(2, 18):
            m[i][i] = 1
            m[i][0] = -int(FF(r) ^ (i - 1))

        m = Matrix(ZZ, m)
        for row in m.LLL():
            if row[0] != 0:
                continue
            # LLL may return either sign of the solution vector.
            for sign in (1, -1):
                raw = [int(sign * row[j]) % 256 for j in range(2, 18)]
                try:
                    candidate = bytes(raw).decode("ascii")
                except (UnicodeDecodeError, ValueError):
                    continue
                if candidate.isprintable():
                    return candidate
    return None


def main():
    h0, h1, h2 = collect_hashes()
    r, s = recover_r_s(h1, h2)
    print(f"Recovered r = {r}")
    print(f"Recovered s = {s}")

    flag = recover_flag(h0, r, s)
    if not flag:
        raise RuntimeError("lattice reduction failed to recover the flag")

    print(f"FLAG: {flag}")


if __name__ == "__main__":
    main()
