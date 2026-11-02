from Crypto.Util.number import bytes_to_long, getStrongPrime
from secret import flag

m = flag

assert len(m) == 255
e = 313
p = getStrongPrime(1024, e=e)
q = getStrongPrime(1024, e=e)

n = p * q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
ct = pow(bytes_to_long(m), e, n)

ctd = pow(d, e, n)
ctpq = (pow(p, e, n) + pow(q, e, n)) % n

print(f"n={n}")
print(f"ctd={ctd}")
print(f"ctpq={ctpq}")
print(f"ct={ct}")
