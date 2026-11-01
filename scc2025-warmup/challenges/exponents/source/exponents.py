from Crypto.Util.number import isPrime

from hidden import p, q, flag
assert isPrime(p) and isPrime(q)

n = p * q
phi = (p-1)*(q-1)
e = 3
d = pow(e, -1, phi)

hint = pow(d, e, phi)
enc = pow(flag, e, n)
print(f"{hint = }")
print(f"{enc = }")
print(f"{n = }")