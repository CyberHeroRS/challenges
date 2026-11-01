import os
from pwn import connect, process, context, remote


FLAG = b'SCC{???????????????????????????????????????????????????}'

mask_len = 2*8*len(FLAG)
max_queries = 2*len(FLAG)*8//5
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

# for _i in range(len(MASK)*8//5):
#     print(depth(int(input()), SECRET))
# print(bytes(x ^ y ^ z for x, y, z in zip(MASK, FLAG, MASK[::-1])).hex())

with remote("10.20.10.10", 9201) as rem:
# with connect('localhost', 1337) as rem:
    def depth_(x):
        # return (depth (x, FLAG_))
        rem.sendline(str(x).encode())
        return int(rem.recvline().decode())
    # s_ = set([0 if depth_(1 << 1) == 1 else 1])
    # queries_count = 1
    s_ = set([0, 1])
    queries_count = 0
    for i in range(1, mask_len -1):
        if len(s_) > 900 or mask_len - i < max_queries - queries_count:
            d = depth_(1 << i+1)
            queries_count += 1
        else:
            d = None    
        s_new = set()
        for s in s_:
            for b in range(2):
                q = (b << i) + s
                if d == None or d == depth(1 << i+1, q + (1 << i+1)):
                    s_new.add(q)
        print(len(s_new), end=' ', flush=True)
        if not s_new:
            print("\nLeading bit of MASK is not 1?", end='')
            break
        s_ = s_new
    
    for _i in range(max_queries - queries_count): depth_(1)

    enc_flag = bytes.fromhex(rem.recvline().decode())
    print(f'\nenc_flag = {enc_flag.hex()}')

    for s in s_:
        MASK = (s + (1 << (i+1))).to_bytes(2*len(FLAG), "big")
        print(f'MASK = {MASK.hex()}')
        print(bytes(x ^ y ^ z for x, y, z in zip(MASK, enc_flag, MASK[::-1])))
