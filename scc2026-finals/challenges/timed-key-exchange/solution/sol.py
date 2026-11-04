# Adapted from the challenge's own checker/tke_solution.py (author-provided).
#
# Note (author's own caveat, preserved): may fail if (time.time_ns() >> 40)
# changes mid-attack -- the server derives its DH exponent `a` from that
# coarse (~18-minute) timestamp bucket XORed with FLAG, so a run straddling
# a bucket boundary would see an inconsistent `a` across connections.
#
# Each connection uses a fresh random prime p (time-salted) but the SAME
# PSK (= shake_256(FLAG) truncated) and generator `h` embedded identically
# into A = g^a * h^PSK mod p. By reconnecting repeatedly and Pohlig-Hellman
# attacking the small (<2^21) factors of each fresh p, we accumulate enough
# CRT'd knowledge of discrete logs base h to recover PSK, then repeat to
# recover the per-session exponent `a`, letting us compute Alice's real
# shared secret and forge a valid "Hello, Alice!" response.
import os
import pwn, json, hashlib
from os import urandom
from math import lcm
from sage.all import Zmod, CRT_list
from sage.rings.factorint import factor_trial_division
from tqdm import tqdm

HOST = os.environ.get("SERVICE_TIMED_KEY_EXCHANGE_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_TIMED_KEY_EXCHANGE_SHELL_PORT", "1337"))


def connect():
    conn = pwn.remote(HOST, PORT)
    return conn

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

def fetch_A():
    conn = connect()
    conn.recvuntil(b'Alice to Bob:')
    m1 = json.loads(conn.recvline().decode().strip())
    p, A = int(m1['p'], 16), int(m1['A'], 16)
    conn.close()
    return p, A

def small_factors(n):
    factors = list(factor_trial_division(n, 1 << 21))
    big_f = factors[-1][0]
    small_factors = [f**m for f, m in factors[:-1]]
    return small_factors

pwn.context.log_level = 'ERROR'
max_order_h = 1
p = 2 << 1023
h = (1 << 127) - 1
g = 2
logs_h = []
orders_h = []
distinguishable_orders_set = set()
visited_factors = set()
with tqdm(total=129) as pbar:
    while max_order_h < (1<<128):
        p, A = fetch_A()
        for s in small_factors(p):
            if s in visited_factors: continue
            visited_factors.add(s)
            Z = Zmod(s)
            hz = Z(h)
            gz = Z(g)
            distinguishable_order = (hz.multiplicative_order()/gz.multiplicative_order()).numerator()
            if distinguishable_order == 1: continue
            if distinguishable_order in distinguishable_orders_set: continue
            Az = Z(A)
            def test(i):
                try: (Az/(hz**i)).log(gz); return True
                except ValueError : return False
            i = next(i for i in range(0,     distinguishable_order) if test(i))
            j = next(j for j in range(i+1, 2*distinguishable_order) if test(j))
            # print('i j j-i', i, j, j-i)
            assert j-i == distinguishable_order
            logs_h.append(j)
            orders_h.append(distinguishable_order)
            distinguishable_orders_set.add(distinguishable_order)
            max_order_h = lcm(max_order_h, orders_h[-1])
            # print(f'm{max_order_h}')
            pbar.n = max_order_h.bit_length()
            pbar.update(0)


PSK = CRT_list(logs_h, orders_h)
print(f'PSK = {PSK}')

max_order = 1
p = 2 << 1024
logs = []
orders = []
with tqdm(total=p.bit_length()) as pbar:
    while max_order < p:
        p, A = fetch_A()
        A = A * pow(h, -PSK, p)
        for s in small_factors(p):
            Z = Zmod(s)
            logs.append(int(Z(A).log(2)))
            orders.append(int(Z(2).multiplicative_order()))
            # print(f'a mod {orders[-1]} = {logs[-1]}')
            max_order = lcm(max_order, orders[-1])
            pbar.n = max_order.bit_length()
            pbar.update(0)
            
a = CRT_list(logs, orders)

conn = connect()
conn.recvuntil(b'Alice to Bob:')
m1 = json.loads(conn.recvline().decode().strip())
p, A = int(m1['p'], 16), int(m1['A'], 16)
conn.recvuntil(b'Bob to Alice:')
m2 = json.loads(conn.recvline().decode().strip())
B = int(m2['B'], 16)
conn.recvline()
conn.recvline()

shared_secret = pow(B * pow(h, -PSK, p), a, p) % p
ciphertext = encrypt(b'Hello, Alice!', shared_secret)
m4 = {'ciphertext' : ciphertext}
conn.sendline(json.dumps(m4))
print(conn.recvline().decode())
conn.close()