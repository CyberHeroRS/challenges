import os

from pwn import *

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))
sol_bytes = open("./input.txt", "rb").read()

p.recvuntil(b'Payload length:\n')
p.sendline(str(len(sol_bytes) + 1).encode())
p.recvuntil(b'Payload:\n')
p.sendline(sol_bytes)
print(p.recvall(timeout=60).decode(errors="replace"))
