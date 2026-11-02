from Crypto.Util.number import *
from math import gcd

flag = b'<REDACTED>'
flag = bytes_to_long(flag)

e1 = 0x10001
e2 = 5

p = getPrime(1024)
q = getPrime(1024)
n = p*q
phi = (p-1)*(q-1)

assert gcd(e1, phi)!=1 
assert gcd(e2, phi)!=1

d1 = inverse(e1, phi)
d2 = inverse(e2, phi)

c = pow(flag, e2, n)

print('n =', n)
print('c =', c)
print('d1 =', d1)
