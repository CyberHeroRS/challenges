"""
Solver for "cross(ed)".

Vulnerability: server.py generates one RSA modulus n = p*q and derives the
private exponent for e1 = 0x10001 as well as e2 = 5, but only ever *uses*
e2 to encrypt the flag (c = flag**e2 mod n). It still happily leaks
d1 = inverse(e1, phi(n)) in the challenge output - i.e. the "friend" handed
out his private key material (d1) alongside the modulus.

Given (n, e1, d1) we can recover phi(n) and factor n in polynomial time
using the standard "factor n from a known (e, d) pair" algorithm (the same
technique used to prove that knowledge of the RSA private exponent is
equivalent to knowing the factorization). Once p and q are known we can
compute the *real* phi(n), invert the exponent that was actually used to
encrypt the flag (e2 = 5), and decrypt c directly - "decrypting messages
other than just his" as the challenge description hints.
"""

import random
from math import gcd

from Crypto.Util.number import long_to_bytes, inverse

# Exponents are hardcoded in public/attachments/server.py; they are not
# part of the per-run output.txt data.
E1 = 0x10001
E2 = 5


def parse_output(path):
    values = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = int(val.strip())
    return values["n"], values["c"], values["d1"]


def factor_from_exponents(n, e, d):
    """Recover a nontrivial factor of n given a known (e, d) key pair."""
    k = e * d - 1
    if k <= 0:
        return None

    t = 0
    s = k
    while s % 2 == 0:
        s //= 2
        t += 1

    for _ in range(200):
        g = random.randint(2, n - 2)
        y = pow(g, s, n)
        if y in (1, n - 1):
            continue
        for _ in range(1, t):
            x = pow(y, 2, n)
            if x == 1:
                p = gcd(y - 1, n)
                if 1 < p < n:
                    return p
                break
            if x == n - 1:
                break
            y = x
    return None


def main():
    n, c, d1 = parse_output("public/attachments/output.txt")

    p = factor_from_exponents(n, E1, d1)
    if p is None:
        raise SystemExit("failed to factor n from the leaked private exponent")

    q = n // p
    assert p * q == n

    phi = (p - 1) * (q - 1)
    d2 = inverse(E2, phi)

    flag_int = pow(c, d2, n)
    flag = long_to_bytes(flag_int)
    print(flag.decode())


if __name__ == "__main__":
    main()
