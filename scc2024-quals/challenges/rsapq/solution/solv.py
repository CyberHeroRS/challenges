#!/usr/bin/env python3
"""
rsapq solver.

Vulnerability
=============
server.py generates a single RSA keypair (p, q, n=p*q, e=313) and, besides the
flag ciphertext `ct = m^e mod n`, it also leaks:

    ctd  = d^e mod n                       (the private exponent, "encrypted" with e)
    ctpq = (p^e + q^e) mod n

Key fact: for n = p*q, the binomial expansion of (p+q)^e mod n collapses,
because every cross term p^i * q^(e-i) with 1 <= i <= e-1 is divisible by
n = p*q. Hence:

    (p + q)^e == p^e + q^e   (mod n)

So ctpq is really `s^e mod n` where s = p + q.

Also, from e*d = 1 + k*phi(n) with phi(n) = n - s + 1, reducing mod n makes the
k*n term vanish:

    e*d == (1 + k) - k*s   (mod n)     for some small unknown integer k in [1, e)

so d == A_k - B_k * s (mod n) for known constants A_k, B_k once k is guessed
(k has only ~e possible values, so this is brute-forceable).

For the correct k, both ctd and ctpq are RSA encryptions (same e, n) of two
values (d and s) related by a known affine relation. This is the classic
Franklin-Reiter related-message attack: build

    g1(x) = (A_k - B_k*x)^e - ctd     (root x = s, using d = A_k - B_k*s)
    g2(x) = x^e - ctpq                (root x = s)

and compute gcd(g1, g2) over Z_n[x]. For the correct k this GCD degenerates to
a linear polynomial (x - s), revealing s = p + q directly. n = p*q and s = p+q
then give p, q via the quadratic formula, and from there phi(n), d, and the
flag.
"""
import math
import sys
from pathlib import Path

import gmpy2
from Crypto.Util.number import long_to_bytes

FLAG_LEN = 255


def parse_output(path):
    values = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = int(val.strip())
    return values["n"], values["ctd"], values["ctpq"], values["ct"]


def trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def polydivmod(a, b, n):
    """Polynomial division a = q*b + r modulo n. Coeffs ascending by power.

    Coefficients are gmpy2.mpz for fast big-integer arithmetic (GMP backend).

    Raises ValueError((factor,)) if a non-trivial factor of n is discovered
    while trying to invert the leading coefficient of b (this directly
    factors n, which also solves the challenge).
    """
    a = trim(a[:])
    b = trim(b[:])
    db = len(b) - 1
    lead_b = b[-1] % n
    g = gmpy2.gcd(lead_b, n)
    if g not in (1, n):
        raise ValueError((int(g),))
    if g == n:
        # lead_b is 0 mod n (shouldn't normally happen); treat as no inverse.
        raise ValueError((None,))
    inv_lead = gmpy2.invert(lead_b, n)
    q = [gmpy2.mpz(0)] * max(len(a) - db, 1)
    while True:
        trim(a)
        da = len(a) - 1
        if da < db or (da == 0 and a[0] == 0):
            break
        coeff = (a[-1] * inv_lead) % n
        shift = da - db
        q[shift] = coeff
        for i in range(db + 1):
            a[shift + i] = (a[shift + i] - coeff * b[i]) % n
        trim(a)
        if len(a) == 1 and a[0] == 0:
            break
    trim(a)
    return q, a


def polygcd(a, b, n):
    a = trim([gmpy2.mpz(c) % n for c in a])
    b = trim([gmpy2.mpz(c) % n for c in b])
    while not (len(b) == 1 and b[0] == 0):
        _, r = polydivmod(a, b, n)
        a, b = b, r
    return a


def affine_power(A, B, e, n):
    """Coeffs (ascending) of (A - B*x)^e mod n."""
    A = gmpy2.mpz(A)
    B = gmpy2.mpz(B)
    coeffs = [gmpy2.mpz(0)] * (e + 1)
    Apow = [gmpy2.mpz(1)] * (e + 1)
    for i in range(1, e + 1):
        Apow[i] = (Apow[i - 1] * A) % n
    Bneg = (-B) % n
    Bpow = [gmpy2.mpz(1)] * (e + 1)
    for i in range(1, e + 1):
        Bpow[i] = (Bpow[i - 1] * Bneg) % n
    for i in range(e + 1):
        coeffs[i] = (gmpy2.mpz(math.comb(e, i)) * Apow[e - i] * Bpow[i]) % n
    return coeffs


def try_factor_from_s(n, s):
    disc = s * s - 4 * n
    if disc < 0:
        return None
    root = math.isqrt(disc)
    if root * root != disc:
        return None
    if (s - root) % 2 != 0:
        return None
    p = (s - root) // 2
    q = (s + root) // 2
    if p * q == n and p > 1 and q > 1:
        return p, q
    return None


def recover_pq(n, e, ctd, ctpq):
    n = gmpy2.mpz(n)
    ctd = gmpy2.mpz(ctd)
    ctpq = gmpy2.mpz(ctpq)
    einv = gmpy2.invert(e, n)
    for k in range(1, e):
        A = (einv * (1 + k)) % n
        B = (einv * k) % n
        g1 = affine_power(A, B, e, n)
        g1[0] = (g1[0] - ctd) % n
        g2 = [gmpy2.mpz(0)] * (e + 1)
        g2[e] = gmpy2.mpz(1)
        g2[0] = (g2[0] - ctpq) % n
        try:
            g = polygcd(g1, g2, n)
        except ValueError as exc:
            (factor,) = exc.args[0] if isinstance(exc.args[0], tuple) else (exc.args[0],)
            if factor and factor not in (1, n):
                factor = int(factor)
                q = int(n) // factor
                if factor * q == int(n):
                    return factor, q
            continue
        if len(g) == 2 and g[1] != 0:
            s = (-g[0] * gmpy2.invert(g[1], n)) % n
            s = int(s)
            factors = try_factor_from_s(int(n), s)
            if factors:
                return factors
            # also consider n - s in case the inverse flipped the sign
            factors = try_factor_from_s(int(n), int(n) - s)
            if factors:
                return factors
    return None


def main():
    here = Path(__file__).resolve().parent
    output_path = here / "output.txt"
    n, ctd, ctpq, ct = parse_output(output_path)
    e = 313

    factors = recover_pq(n, e, ctd, ctpq)
    if not factors:
        print("Failed to recover p, q", file=sys.stderr)
        sys.exit(1)
    p, q = factors
    assert p * q == n

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(ct, d, n)
    flag = long_to_bytes(m, FLAG_LEN)
    print(flag.decode())


if __name__ == "__main__":
    main()
