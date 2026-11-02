from hashlib import sha512
from os import urandom

flag = REDACTED

def xor(a, b):
    return bytes([x^y for x,y in zip(a,b)])

f = open("out.txt", "wb")

for _ in range(32):
    random_bytes = urandom(len(flag))
    random_hash = sha512(random_bytes).hexdigest().encode()
    xored_flag = xor(flag, random_hash)
    f.write(xored_flag)

f.close()