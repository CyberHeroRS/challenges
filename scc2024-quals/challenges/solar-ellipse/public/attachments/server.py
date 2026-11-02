import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import *
from sage.all import *
from secret import a, b, n

iv = os.urandom(16)

flag = b'<REDACTED>'

p = getPrime(150)
kx = GF(p).random_element()
ky = GF(p).random_element()

EC = EllipticCurve(GF(p), [a, b])

A = EC.random_point()
B = EC.lift_x(n)

k = EC(kx, ky)
C = EC(ky**n, kx**n)

key = long_to_bytes(int(ky))[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
ct = (iv + cipher.encrypt(pad(flag, 16))).hex()

f = open('out.txt','w')
f.write(f'A = {A}\n')
f.write(f'B = {B}\n')
f.write(f'p = {p}\n')
f.write(f'ct = {ct}\n')
f.close()