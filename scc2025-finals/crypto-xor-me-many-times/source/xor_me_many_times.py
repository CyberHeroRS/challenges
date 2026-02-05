import os

FLAG = os.environ.get('FLAG', 'SCC{???????????????????????????????????????????????????}').encode()
MASK = os.urandom(2*len(FLAG))
SECRET = int.from_bytes(MASK, "big")

def depth(a, b):
    if a < b: a, b = b, a
    i = 0
    while b > 0:
        bl = b.bit_length()
        while a >= b:
            a ^= b << (a.bit_length() - bl)
        i += 1
        a, b = b, a
    return i

for _i in range(len(MASK)*8//5):
    print(depth(int(input()), SECRET))

print(bytes(x ^ y ^ z for x, y, z in zip(MASK, FLAG, MASK[::-1])).hex())
