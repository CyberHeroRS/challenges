"""Solver for "The Three-Encryption Problem".

Recap of the scheme (see public/source.py):

    e = 33
    p, q = getPrime(128), getPrime(128)
    n = p * q
    for idx in range(0, len(flag), 3):
        e1 = pow(flag[idx],   e, p)
        e2 = pow(flag[idx+1], e, q)
        e3 = pow(flag[idx+2], e, n)
        print(e1 * e2 * e3)

Each printed value is the *product* of three independent, differently
moduli-reduced "encryptions" of three consecutive flag bytes. There is no
final reduction of that product, which is the crack in the scheme:

1. Every flag byte is printable ASCII (32-126), so byte**33 is at most
   ~2**231. n = p*q is at least ~2**254 (both p, q are 128-bit primes), so
   byte**33 is *always* smaller than n: e3 is never actually reduced, it is
   exactly c2**33. That means the third character of every triplet can be
   recovered on its own by brute-forcing printable candidates and checking
   which one divides the printed value evenly.

2. Dividing that factor out leaves M = e1 * e2, with e1 = c0**33 mod p and
   e2 = c1**33 mod q for the still-unknown first/second characters. p and q
   are fixed for the whole message, so whenever two different lines reuse
   the same character in the c0 (or c1) slot -- very common in a flag, full
   of underscores/digits -- their M values share the common factor e1 (or
   e2). Clustering lines by a large pairwise gcd(M_i, M_j) finds these
   repeats; intersecting a whole cluster isolates the shared residue.

3. A residue recovered this way can carry a small leftover factor shared by
   the *other* (unrelated) values in the cluster (e.g. all the involved e2
   values happen to be even). Stripping every small prime factor (<=97) and
   keeping each possible "de-contaminated" variant covers that.

4. For two different clusters belonging to the *same* modulus (both c0-type
   or both c1-type), trying every printable character against every
   de-contaminated residue and computing
       gcd(x**33 - residue_a, y**33 - residue_b)
   eventually lands on p (or q) itself, possibly times a tiny leftover
   factor that a final small-prime cleanup removes. This is done without
   ever knowing which character produced which residue, or which modulus
   (p or q) a cluster belongs to -- both are discovered purely from the
   ciphertext.

5. With p and q in hand, every line is solved independently: reuse the
   exact c2 from step 1, brute force c0 over printable characters (check
   M % pow(c0, 33, p) == 0) and look the leftover quotient up in a
   precomputed c1 table.
"""

import sys
from itertools import combinations
from math import gcd

E = 33
PRINTABLE = list(range(32, 127))
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)


def small_factor_variants(n, limit=97):
    """All values n // d, where d ranges over every divisor of n built purely
    from prime factors <= limit (including d = 1, i.e. n itself)."""
    rem = n
    factors = []
    d = 2
    while d <= limit:
        while rem % d == 0:
            factors.append(d)
            rem //= d
        d += 1
    divisors = {1}
    for f in set(factors):
        count = factors.count(f)
        extended = set()
        for existing in divisors:
            power = 1
            for _ in range(count + 1):
                extended.add(existing * power)
                power *= f
        divisors = extended
    return [n // d for d in divisors]


def is_probable_prime(n, rounds=20):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    import random

    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def strip_small_factors(n, min_bits=120):
    """Repeatedly divide out small prime factors while the remainder still
    looks like it could be the modulus we're after."""
    cand = n
    changed = True
    while changed:
        changed = False
        for sp in SMALL_PRIMES:
            while cand % sp == 0 and (cand // sp).bit_length() >= min_bits:
                cand //= sp
                changed = True
    return cand


def recover_moduli(values):
    pow33 = {c: pow(c, E) for c in PRINTABLE}

    # Step 1: recover the exact e3 factor (and thus M = e1 * e2) wherever
    # the printable-character candidate is unambiguous.
    M = {}
    c2_candidates = {}
    for i, V in enumerate(values):
        cands = [c for c in PRINTABLE if V % pow33[c] == 0]
        c2_candidates[i] = cands
        if len(cands) == 1:
            M[i] = V // pow33[cands[0]]

    idxs = sorted(M)

    # Step 2: cluster lines whose M values share a large common factor,
    # i.e. that reused the same plaintext character in the c0 or c1 slot.
    parent = {i: i for i in idxs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, j in combinations(idxs, 2):
        if gcd(M[i], M[j]).bit_length() > 100:
            union(i, j)

    clusters = {}
    for i in idxs:
        clusters.setdefault(find(i), []).append(i)
    clusters = [members for members in clusters.values() if len(members) > 1]

    cores = []
    for members in clusters:
        core = 0
        for m in members:
            core = gcd(core, M[m])
        cores.append(core)

    core_variants = [small_factor_variants(c) for c in cores]

    # Step 3: brute force character/cluster pairs to recover 128-bit moduli.
    moduli = []
    for a, b in combinations(range(len(cores)), 2):
        for x in PRINTABLE:
            dxs = [pow33[x] - ca for ca in core_variants[a]]
            for y in PRINTABLE:
                dys = [pow33[y] - cb for cb in core_variants[b]]
                for dx in dxs:
                    for dy in dys:
                        g = gcd(dx, dy)
                        if g.bit_length() < 120:
                            continue
                        cand = strip_small_factors(g)
                        if cand.bit_length() in (127, 128) and is_probable_prime(cand):
                            if cand not in moduli:
                                moduli.append(cand)

    return moduli, pow33, c2_candidates


def try_decode(values, p, q, pow33, c2_candidates):
    e2_table = {pow(c, E, q): c for c in PRINTABLE}

    flag_bytes = bytearray()
    for i, V in enumerate(values):
        solved = False
        for c2 in c2_candidates[i]:
            Mi = V // pow33[c2]
            for c0 in PRINTABLE:
                e1 = pow(c0, E, p)
                if e1 and Mi % e1 == 0:
                    rem = Mi // e1
                    if rem in e2_table:
                        flag_bytes += bytes([c0, e2_table[rem], c2])
                        solved = True
                        break
            if solved:
                break
        if not solved:
            return None
    try:
        return flag_bytes.decode("ascii")
    except UnicodeDecodeError:
        return None


def main():
    with open("out.txt") as f:
        values = [int(line) for line in f.read().split()]

    moduli, pow33, c2_candidates = recover_moduli(values)
    if len(moduli) < 2:
        sys.exit("failed to recover the two RSA-like moduli p and q")

    for p, q in combinations(moduli, 2):
        for ordered in ((p, q), (q, p)):
            flag = try_decode(values, *ordered, pow33, c2_candidates)
            if flag is not None and flag.isprintable():
                print(flag)
                return

    sys.exit("recovered candidate moduli but could not decode a full flag")


if __name__ == "__main__":
    main()
