from pwn import *

p = remote("localhost", 5000)

for i in range(500):
    p.recvuntil(b"Round ")
    equation = p.recvuntil(b" =").split(b" ")
    solution = int(equation[1]) + int(equation[3])
    p.sendline(str(solution).encode())

p.interactive()
