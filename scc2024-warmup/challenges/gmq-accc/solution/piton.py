import os

from pwn import *

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

for i in range(500):
    p.recvuntil(b"Round ")
    equation = p.recvuntil(b" =").split(b" ")
    solution = int(equation[1]) + int(equation[3])
    p.sendline(str(solution).encode())

print(p.recvall().decode())
