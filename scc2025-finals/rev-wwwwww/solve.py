from pwn import *

# p = process('target/release/wwwwww')
p = remote('10.20.10.10', 9207)
p.sendline(open("moves.txt").read())
success(p.recvall(0.2).decode())
