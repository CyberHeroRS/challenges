"""
Solver for "solar ellipse".

Vulnerability
-------------
server.py builds an elliptic curve EC = EllipticCurve(GF(p), [a, b]) with
*secret* coefficients a, b and a secret value n, then leaks:

  A = EC.random_point()      -- a random point ON the curve
  B = EC.lift_x(n)            -- a point whose x-coordinate IS n

1. n is leaked directly: B.x() == n, no attack needed.
2. a, b are each only linear unknowns appearing in TWO known-point
   equations (A and B both satisfy y^2 = x^3 + a*x + b mod p), so they are
   recovered by solving that tiny linear system (the "system of
   polynomials" the flag/name hints at).
3. The AES key is `long_to_bytes(ky)[:16]` where (kx, ky) are the
   coordinates of a secret point K, constrained by the script itself
   requiring BOTH:
       ky^2 == kx^3 + a*kx + b                      (K on the curve)
       (kx^n)^2 == (ky^n)^3 + a*(ky^n) + b           (C=(ky^n,kx^n) on it)
   Treating kx as a formal root of the first (cubic) equation, we reduce
   kx^n modulo that cubic via fast exponentiation (coefficients become
   polynomials in ky only), plug into the second equation, and eliminate
   kx with a resultant. This yields a univariate polynomial in ky alone;
   its root(s) over GF(p) recover ky (and from it kx, via the cubic).
4. ky directly gives the AES-CBC key used to encrypt the flag.
"""

import re
import time
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import unpad

with open('out.txt') as f:
    data = f.read()

def parse_point(name):
    m = re.search(rf'{name} = \((-?\d+) : (-?\d+) : (\d+)\)', data)
    return int(m.group(1)), int(m.group(2))

Ax, Ay = parse_point('A')
Bx, By = parse_point('B')
p = int(re.search(r'p = (\d+)', data).group(1))
ct_hex = re.search(r'ct = ([0-9a-f]+)', data).group(1)

print(f"p  = {p}")
print(f"A  = ({Ax}, {Ay})")
print(f"B  = ({Bx}, {By})")

GFp = GF(p)
xa, ya, xb, yb = GFp(Ax), GFp(Ay), GFp(Bx), GFp(By)

# --- Step 1: n is simply B's x-coordinate (EC.lift_x(n) sets x == n). ---
n = Bx
print(f"recovered n = {n}")

# --- Step 2: solve the linear system for a, b from points A and B. ---
# yA^2 = xA^3 + a*xA + b
# yB^2 = xB^3 + a*xB + b
a = ((ya**2 - yb**2) - (xa**3 - xb**3)) / (xa - xb)
b = ya**2 - xa**3 - a * xa
print(f"recovered a = {a}")
print(f"recovered b = {b}")

EC = EllipticCurve(GFp, [a, b])
assert EC(Ax, Ay) == EC(Ax, Ay), "A sanity check"
assert EC(Bx, By) == EC(Bx, By), "B sanity check"

# --- Step 3: eliminate kx via resultant to recover ky. ---
t0 = time.time()
P = PolynomialRing(GFp, 'ky')
ky = P.gen()
Px = PolynomialRing(P, 'x')
x = Px.gen()

f1 = x**3 + a * x + b - ky**2  # K=(x,ky) on curve

def powmod(base, e, mod):
    result = Px(1)
    base = base % mod
    while e > 0:
        if e & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        e >>= 1
    return result

xn = powmod(x, n, f1)                      # kx^n mod f1, deg <= 2 in x
RHS = ky**(3 * n) + a * ky**n + b          # (ky^n)^3 + a*(ky^n) + b
g = (xn * xn) % f1 - Px(RHS)               # C on curve constraint, deg <= 2 in x

R = f1.resultant(g)                        # eliminate x -> polynomial in ky
print(f"resultant computed in {time.time() - t0:.1f}s, degree {R.degree()}")

pari.allocatemem(2 * 1024 * 1024 * 1024, 16 * 1024 * 1024 * 1024)

t1 = time.time()
roots = R.roots(multiplicities=False)
print(f"root finding took {time.time() - t1:.1f}s, found {len(roots)} candidate(s)")
roots = [(r, 1) for r in roots]

Pxp = PolynomialRing(GFp, 'xk')
xk = Pxp.gen()

flag = None
for ky0, _ in roots:
    cubic = xk**3 + a * xk + b - ky0**2
    for kx0, _ in cubic.roots():
        try:
            EC(kx0, ky0)
            EC(ky0**n, kx0**n)
        except (ValueError, TypeError):
            continue

        key = long_to_bytes(int(ky0))[:16]
        raw = bytes.fromhex(ct_hex)
        iv, ct = raw[:16], raw[16:]
        pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
        try:
            candidate = unpad(pt, 16)
        except ValueError:
            continue
        if candidate.startswith(b'SCC{') or candidate.startswith(b'<REDACTED'):
            flag = candidate
            break
    if flag:
        break

if flag is None:
    raise SystemExit("failed to recover the flag")

print(f"FLAG: {flag.decode()}")
