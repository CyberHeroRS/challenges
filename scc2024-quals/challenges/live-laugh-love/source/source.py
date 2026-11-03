from Crypto.Cipher import DES3

import os
from os import urandom

# Injected via challenge.yaml's env-based flag mechanism (already wrapped in
# the event's flag format, e.g. "SCC{...}"). The Poly2585 lattice attack
# used by this challenge's solver hardcodes a 16-byte message length, so the
# configured flag body/prefix/format must keep the wrapped flag at exactly
# 16 bytes (as it already does: "SCC{sh0rt_FL4g!}" == 16 bytes).
FLAG = os.environ.get("FLAG", "SCC{dev_test!!!}").encode()
assert len(FLAG) == 16

def derive(key):
    r = key[:16]
    s = DES3.new(key[8:], mode=DES3.MODE_ECB).encrypt(r)
    return int(r.hex(),16), int(s.hex(),16)

def poly2585(msg, r, s):
    f = 0
    mod = pow(2,258) - 5
    for idx, m in enumerate(msg):
        f += pow(r, idx+1, mod) * m
        f %= mod
    f = (f + s) % mod
    return f % pow(2,256)

def better_hash(msg, key):
    r, s = derive(key)
    h = poly2585(msg, r, s)
    return hex(h)

if __name__ == "__main__":
    x = urandom(16)
    print("Welcome to Poly2585 - a much safer hash family!")
    print("I'll even let you have control over the secrets so you can see how secure it is!")

    try:
        part1 = bytes.fromhex(input("Suffix of the first key: "))
        part2 = bytes.fromhex(input("Suffix of the second key: "))
        m1 = bytes.fromhex(input("First message to hash: "))
        m2 = bytes.fromhex(input("Second message to hash: "))
    
        assert len(part1) == 8 == len(part2)
        assert m1 != m2
    
    except (ValueError, AssertionError):
        print("Something went wrong")
        exit()

    key1 = x + part1
    key2 = x + part2

    print("\nKeys made... now hashing!")

    h = better_hash(FLAG, key1)
    print(f"{h = }")
    
    h = better_hash(m1, key2)
    print(f"{h = }")

    h = better_hash(m2, key2)
    print(f"{h = }")
