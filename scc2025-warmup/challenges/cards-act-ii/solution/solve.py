import os

from pwn import remote

p = 1054510945910607851467964685929741094129513043460423391244893493596392448882307 # prime
assert (p-1)%3 == 0
t = (p-1)//3

g = 11
gt = pow(g, t, p)

SUCCESS = False

while not SUCCESS:
    io = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))
    io.sendline(hex(p)[2:].encode())
    io.sendline(hex(gt)[2:].encode())

    # Random state will set g to either itself, g^2, or 1
    # We assume it'll be 1
    state = 1

    from cards import NextGenRandom, Card, SUITS
    ngr = NextGenRandom(gt, p)
    ngr.state = 1

    for _ in range(50):
        current_card = Card(5, SUITS[0])
        new_card = ngr.next_card()

        if (new_card.value > current_card.value):
            io.sendline(b"y")
        else:
            io.sendline(b"n")

    res = io.recvall()[-32:]
    if b"SCC" in res:
        SUCCESS = True
        break

print(res)
