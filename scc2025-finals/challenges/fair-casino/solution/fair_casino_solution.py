from hashlib import sha1, md5
from secrets import randbits, randbelow
import os
from tqdm import tqdm
from pwn import process, remote, connect, context

# context.log_level = 'debug'
SIZE = 7

def find_collision_(gambler_id, choice_byte, bit):
    assert 0 <= choice_byte < SIZE
    assert 0 <= bit <= 7
    mask = 1 << bit

    def f(x):
        if x[choice_byte] & mask:
            return sha1(gambler_id+x).digest()[:SIZE]
        else:
            return md5(gambler_id+x).digest()[:SIZE]
    
    def hash_type(x):
        return 'sha' if x[choice_byte] & mask else 'md5'

    x0 = os.urandom(SIZE)
    x = x0
    y = x0
    print(f'x0 = {x0.hex()}')

    for i in tqdm(range(1<<(4*SIZE))):
        x = f(x)
        y = f(f(y))
        if x == y:
            break
    if x != y: return

    x = x0
    for i in tqdm(range(1<<(4*SIZE))):
        old = x, y
        x = f(x)
        y = f(y)
        if x == y:
            break
    if x != y: return
    x, y = old
    assert x != y
    
    print(f'type x = {hash_type(x)} {x}')
    print(f'type y = {hash_type(y)} {y}')
    if hash_type(x) != hash_type(y):
        return (x, y) if hash_type(x) == 'sha' else (y, x)

def find_collision(gambler_id):
    for i in range(1, 20):
        print(f'Try #{i}')
        bit = randbelow(8)
        choice_byte = randbelow(SIZE)
        coll =  find_collision_(gambler_id, choice_byte, bit)
        if coll: return coll
    return

for _i in range(10):
    with remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"])) as rem:
    # with connect('localhost', 1337) as rem:
        rem.recvuntil(b'Wellcome ')
        gambler_id = int(rem.recvline().decode()[:19])
        print(f'gambler_id = {gambler_id}')
        r = find_collision_(gambler_id.to_bytes(8), 0, 0)
        if r:
            x, y = r
            for i in range(60):
                print(f'round #{i}')
                rem.recvuntil(b'Place your bet (black|red): ')
                rem.sendline(b'red')
                rem.recvuntil(b'Bet ammount: ')
                rem.sendline(str(int(100 * 1.79**i)).encode())
                rem.recvuntil(b'Your commitment: ')
                c = sha1(gambler_id.to_bytes(8) + x).digest()[:SIZE].hex()
                rem.sendline(c)
                B = b'red' in rem.recvline()
                rem.recvuntil(b'Your roulette ball lands on (black|red): ')
                rem.sendline(b'red' if not B else b'black')
                rem.recvuntil(b'Your decommitment: ')
                rem.sendline((x if not B else y).hex())
                print(rem.recvline())

            print(rem.recvline())
            break