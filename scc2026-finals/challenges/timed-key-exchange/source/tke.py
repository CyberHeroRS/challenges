import hashlib, json, time
from os import urandom, environ

def xor(x, y): return bytes(bx ^ by for bx, by in zip(x, y))

def encrypt(plaintext, shared_secret):
    IV = urandom(16)
    shake = hashlib.shake_256(IV + shared_secret.to_bytes(128))
    stream = shake.digest(len(plaintext))
    cipertext = IV.hex(), xor(stream, plaintext).hex()
    return cipertext

def decrypt(cipertext, shared_secret):
    IV, ctx = bytes.fromhex(cipertext[0]), bytes.fromhex(cipertext[1])
    shake = hashlib.shake_256(IV + shared_secret.to_bytes(128))
    stream = shake.digest(len(ctx))
    plaintext = xor(stream, ctx)
    return plaintext


FLAG = environ.get('FLAG', 'SCC{test}')
p = ((1 << 1023) + time.time_ns()) | 1
g = 2
h = (1 << 127) - 1

PSK = int.from_bytes(hashlib.shake_256(FLAG.encode()).digest(16))
# print(PSK)
shake = hashlib.shake_256((time.time_ns() >> 40).to_bytes(16) + FLAG.encode())
a = int.from_bytes(shake.digest(32))
A = pow(g, a, p) * pow(h, PSK, p) % p
m1 = {'p' : hex(p), 'g' : hex(g), 'A' : hex(A)}
print('Alice to Bob:', json.dumps(m1))

b = int.from_bytes(urandom(32))
B = pow(g, b, p) * pow(h, PSK, p) % p # use different h
m2 = {'B' : hex(B)}
print('Bob to Alice:', json.dumps(m2))

shared_secret = pow(B * pow(h, -PSK, p), a, p) % p
ciphertext = encrypt(b'Hi, Bob. How are you doing?', shared_secret)
m3 = {'ciphertext' : ciphertext}
print('Alice to Bob:', json.dumps(m3))

try:
    print(f'Eve (impersonating Bob) to Alice:')
    m4 = json.loads(input())
    plaintext = decrypt(m4['ciphertext'], shared_secret)

    if b'Hello, Alice!' not in plaintext:
        print('Booooooooooob! Help me, this should not have been possible.')
        print('Someone is attacking me.')
        exit()

    if bytes.fromhex(ciphertext[0]) == bytes.fromhex(m4['ciphertext'][0]):
        print('Bob, you should know better than this.')
        print('Reusing initialization vectors is a cryptographic sin.')
        exit()
    
    print(f'Here is the secret: {FLAG}')

except json.JSONDecodeError:
    print('Error while decoding JSON.')
    exit()

except Exception:
    print(f'Fatal error.')
    exit()

