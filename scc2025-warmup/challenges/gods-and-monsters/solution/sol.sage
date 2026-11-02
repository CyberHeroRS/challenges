"""
Solver for "Gods & Monsters".

Vulnerability
-------------
gods_and_monsters.py implements elliptic-curve point addition/doubling by
hand using explicit formulae full of "magic number" constants, instead of
naming the curve. Those constants are exactly the a1/a2/a3/a4/a6
coefficients of a general Weierstrass curve
    y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6
(see https://crypto.stanford.edu/pbc/notes/elliptic/explicit.html for the
textbook formulae they were copied from). Once the curve is identified,
the generator G's order turns out to be smooth enough to attack directly:
Pohlig-Hellman recovers the discrete log n modulo the smooth part of the
order (~64 bits), and the tiny remaining unknown (~5-6 bits, bounded by
`assert n < 2**70` in the source) is simply brute forced.

n is the shared secret used (via sha256) as the AES-CBC key that encrypts
the flag, so recovering n recovers the flag.
"""

import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha256

with open('out.txt') as f:
    data = f.read()


def parse_point(name):
    m = re.search(rf'{name} = Point\((\d+), (\d+)\)', data)
    return int(m.group(1)), int(m.group(2))


Gx, Gy = parse_point('G')
Px, Py = parse_point('P')
enc_hex = re.search(r"enc = '([0-9a-f]+)'", data).group(1)
iv_hex = re.search(r"iv = '([0-9a-f]+)'", data).group(1)

print(f"G = ({Gx}, {Gy})")
print(f"P = ({Px}, {Py})")

# --- Curve parameters, recovered from the magic numbers in gods_and_monsters.py ---
p = 67971422875209843218823497319855231593203446798693404917904261220233138364877
a1 = 1
a2 = 27723118983053438240314554566919304702009372842675523657054796985533101035967
a3 = 36705335186416557299559736926700113135726096437924011941539879171053079785019
a4 = 13135011342158767390972930743879758669664065038225826254653566661198441680369
a6 = 45493736686359268253421923085820265975471414362134679444217955415112786078568

EC = EllipticCurve(GF(p), [a1, a2, a3, a4, a6])
G = EC(Gx, Gy)
P = EC(Px, Py)

# --- Pohlig-Hellman on the smooth part of the generator's order ---
o = G.order()
print(f"order factorization: {o.factor()}")

facs = list(o.factor())
mods, rems = [], []
for prime, exp in facs[:-1]:
    t = prime ** exp
    v = o // t
    r = (P * v).log(G * v)
    mods.append(t)
    rems.append(r)

# The last (largest-cofactor / smallest-order) factor is too small to help
# Pohlig-Hellman meaningfully; it's left as the brute-forced remainder.
last_prime, last_exp = facs[-1]
a = last_prime ** last_exp

n_ = crt(rems, mods)
step = o // a
while n_ * G != P:
    n_ += step

n = int(n_)
print(f"recovered n = {n}")

key = sha256(str(n).encode()).digest()[:16]
raw = bytes.fromhex(enc_hex)
iv = bytes.fromhex(iv_hex)
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(raw)
flag = unpad(pt, 16).decode()
print(f"FLAG: {flag}")
