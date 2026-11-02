import os

from pwn import *

# p = process('source/target/release/wwwwww')
p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))
p.sendline(open("solution/moves.txt").read())
success(p.recvall(0.2).decode())
