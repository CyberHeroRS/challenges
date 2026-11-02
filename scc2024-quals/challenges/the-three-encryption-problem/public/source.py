from Crypto.Util.number import getPrime

flag = REDACTED

e = 33
p, q = getPrime(128), getPrime(128)
n = p*q

for idx in range(0, len(flag), 3):
    e1 = pow(flag[idx], e, p)
    e2 = pow(flag[idx + 1], e, q)
    e3 = pow(flag[idx + 2], e, n)

    print(e1*e2*e3)