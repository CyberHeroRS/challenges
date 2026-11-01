from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import getPrime
from gmpy2 import mpz
from time import time
from os import urandom, environ

FLAG = environ.get('FLAG', 'SCC{???????????????????????????????????????????????????}').encode()
e = 3

while True:
    p = mpz(getPrime(512))
    q = mpz(getPrime(512))
    if (p-1) % e != 0 and (q-1) % e != 0: break

l = 4096
N = p*q**l
print(f'p = {p}')
print(f'N = {N}')

K = urandom(N.bit_length()//8)
m = mpz(int.from_bytes(K))

t = time()
c = pow(m, e, N)
print(f'c = {c}')

key, iv = K[-16:], K[-32:-16]
cipher = AES.new(key, AES.MODE_CBC, iv)
ct = cipher.encrypt(pad(FLAG, 16))
print(f'ct = {ct.hex()}')
