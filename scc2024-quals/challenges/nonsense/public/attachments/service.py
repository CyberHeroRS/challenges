from sage.all import *
from Crypto.Util.number import getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256
from secret import a, b

FLAG = b'<REDACTED>'
flag_len = len(FLAG)

nbits = 17
p = getPrime(nbits)

Dn = DihedralGroup(p)
g = Dn.gens()[0]

A = g**a
B = g**b

shared_a = A**b
shared_b = B**a

    # FLAG enc
key = sha256(str(shared_a).encode()).digest()
cipher = AES.new(key, AES.MODE_ECB)
c = cipher.encrypt(pad(FLAG, 16))

with open('output.txt', 'a') as f:
    f.write(f'{p = }\n')
    f.write(f'{g = }\n')
    f.write(f'{A = }\n')
    f.write(f'{B = }\n')
    f.write(f'{c = }\n')
