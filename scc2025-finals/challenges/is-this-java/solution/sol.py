"""Solver for `isthisjava`.

`isthisjava` is a REV challenge: it encodes a fixed directed graph by
(ab)using one C++ class per vertex/edge, with multiple inheritance and
virtual dispatch standing in for graph edges. Every byte typed on stdin
picks which base-class ("edge") the current vertex object hands control to
next; reaching vertex 99 with an accumulated value equal to its hard-coded
target prints the flag.

The graph is recovered genuinely from the real binary at solve time -- see
recover_graph.py for the full algorithm (an IDA-free reimplementation, via
pyelftools + Capstone, of the original RTTI/vtable-structure graph recovery
that was prototyped once in IDAPython) -- then a Dijkstra shortest path from
vertex 0 to vertex 99 over that freshly-recovered graph gives us the magic
input string. Nothing here is precomputed or hardcoded: every run of this
solver re-derives the input from scratch by analyzing the binary.

`source/chall/isthisjava` is a fixed artifact: gen.py was run once at
challenge authoring time to produce source/src.cpp with ONE fixed random
graph, which is compiled and the resulting binary is baked into the service
image verbatim (the service Dockerfile just COPYs chall/isthisjava, it never
re-runs gen.py). So the graph never changes between runs of this binary, and
re-deriving the magic input at solve time is cheap and correctness-verified.
We still pin the binary's hash below, so the test fails loudly instead of
silently if that ever stops being true.
"""

import hashlib
import os

from pwn import *

from recover_graph import compute_magic_input

BINARY_PATH = "/solution/isthisjava"
# sha256 of the binary the graph-recovery algorithm was validated against, so
# a future regeneration of the challenge binary makes this test fail loudly
# instead of silently trusting an unverified analysis.
EXPECTED_SHA256 = "e5978ecf75481e324de7f268ad42bab760018cf74d18d9f408edd088bb3739c0"

if os.path.exists(BINARY_PATH):
    with open(BINARY_PATH, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()
    assert actual_sha256 == EXPECTED_SHA256, (
        f"isthisjava binary changed (sha256 {actual_sha256}), "
        "the graph-recovery algorithm needs to be re-validated against it"
    )

magic_input = compute_magic_input(BINARY_PATH)
print(f"computed magic input: {magic_input.decode()}")

host = os.environ["SERVICE_APP_MAIN_HOST"]
port = int(os.environ["SERVICE_APP_MAIN_PORT"])

p = remote(host, port)
p.send(magic_input)
print(p.recvall(timeout=10).decode(errors="replace"))
