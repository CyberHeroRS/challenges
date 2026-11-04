import os

from pwn import context, remote

# STATUS: NOT YET WORKING -- no solve script implemented yet, just the
# cryptographic analysis needed to build one. Documented here instead of
# left as a bare stub so whoever picks this up doesn't have to re-derive
# the structure from scratch.
#
# "Patrick" is a custom sponge-like MAC:
#   state (3 bytes) starts at 0; absorb_block(block):
#     state = AES_key1_encrypt(pad(state ^ block, 16))[:3]
#   finalize():
#     state = AES_key1_encrypt(pad(state, 16))      # full 16-byte block now
#     state = AES_key2_decrypt(state)
#     tag   = AES_key3_encrypt(state)
#     state reset to 0; return tag
#
# Each of key1/key2/key3 is derived as:
#   get_random_bytes(3).hex() * 2 + "KEY<n>"
# i.e. only 3 TRUE random bytes (literally repeated twice) + a fixed
# known suffix -- each key has only 2**24 possible values, not 2**128.
#
# The server computes target_tag = Patrick(key1,key2,key3).absorb(b"spongebob").finalize()
# ONCE at startup, then exposes an oracle: send arbitrary hex bytes (not
# containing the literal substring "spongebob") and get back
# Patrick(key1,key2,key3).absorb(data).finalize() for YOUR chosen data
# (state always starts fresh at 0, since finalize() resets it). Sending
# a hex string that decodes to data containing "spongebob" anywhere
# instead prompts for a guess at target_tag directly.
#
# We cannot replay the literal 3 blocks ("spo","nge","bob") through the
# oracle to recover target_tag directly -- any data producing that exact
# absorption sequence IS "spongebob" and triggers the forbidden branch
# instead of returning a tag. So the only way to compute target_tag
# ourselves is to fully recover key1, key2, key3 and run the whole
# Patrick construction OFFLINE on b"spongebob" (no live interaction
# needed for that final step), then send the resulting tag as our guess.
#
# Progress so far:
#   - data="" skips the absorb loop entirely (range(0, 0, 3) is empty),
#     so the state entering finalize() is ALWAYS exactly b"\x00\x00\x00"
#     for that one query -- independent of key1 (no absorption occurs).
#     This gives ONE clean known-plaintext relation through the full
#     3-key pipeline: TAG_A = key3_enc(key2_dec(key1_enc(P0))), where
#     P0 = pad(b"\x00\x00\x00", 16) is fully known.
#   - Every OTHER query's entering-state depends on key1 (via at least
#     one absorb_block call), so it is not independently "clean" --
#     recovering a second, key1-independent known-plaintext pair this
#     way does not appear possible; any second data point still has
#     key1 baked into how its entering-state was produced.
#   - This leaves a single 3-unknown equation
#     (key1, key2, key3, each 2**24) chained through 3 AES calls with no
#     unforgeable shortcut I've found yet to split it into a clean
#     2-table O(2**24) meet-in-the-middle (the natural middle point
#     between key1's output and key2/key3's combined effect still
#     requires knowing key1 first to compute, and vice versa).
#
# Next step for whoever picks this up: either find a second genuinely
# key1-independent (plaintext, tag) pair through the oracle (if one
# exists, it would turn this into a standard 2-meeting-point MITM
# across 3 AES stages, each side only 2**24), or confirm the intended
# solution really does require an O(2**48)-ish search (feasible with a
# fast/parallelized implementation, impractical in a plain Python test
# container) and implement accordingly.

HOST = os.environ.get("SERVICE_PATRICK_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_PATRICK_SHELL_PORT", "1337"))

raise SystemExit("exploit not yet implemented -- see header comment for analysis so far")
