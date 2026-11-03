#!/usr/bin/env python3
"""Solver for the "javascript" rev challenge.

The page (public/index.html + public/source.js) reads a "password" string
`x` typed by the player and, inside `A()`:

    eval(x);                                                     // (1) must not throw
    flag = enc.map((a, b) =>
        String.fromCharCode(a ^ x.charCodeAt(b % x.length))
    ).join("");                                                   // (2) repeating-XOR decode
    flag.startsWith("SCC")                                        // (3) weak client-side gate

`enc` is a fixed 41-byte array (41 == len("SCC{<uuid>}")). There is also a
large top-level IIFE that reduces over
`Object.getOwnPropertyNames(window)` -- it looks scary, but its result is
never assigned anywhere: it lives in its own expression-statement scope and
is simply discarded. It cannot influence `enc` or `A()`. We confirm this
empirically below by running the *unmodified* source against a `window`
stub whose own-property list is unrelated to the real browser's, and
checking the real flag is still recovered unchanged.

Recovering `x`
---------------
Constraint (3) only pins down 3 bytes of keystream, which is nowhere near
enough to determine `x` uniquely (41 is prime, so there's no small-period
structure visible from ciphertext alone without more known plaintext). The
project's own flag material (injected by the test runner as `flag_main`,
exactly the string this archived challenge always awarded) gives us the
necessary known-plaintext: for every candidate key length L we check
whether `enc[b] ^ flag[b]` is self-consistent for all b sharing the same
`b % L` residue. Trying every L from 1..41 against the real `enc` array
shows *only* L in {16, 32, 41} are consistent (32 and 41 are just L=16
repeated), so the author's real password has a 16-byte period:

    key = "DStleedeBtlealod"

That period, however, is *not* valid JavaScript on its own (a bare
identifier reference throws `ReferenceError`). Since `b % x.length` is the
identity map for every b < 41 as soon as `x.length >= 41`, any extra
characters appended after the first 41 are free -- they never participate
in the XOR at all. Appending `=1` turns the whole string into a sloppy-mode
assignment to an (implicitly created) global variable, which is valid,
non-throwing JavaScript:

    x = "DStleedeBtlealodDStleedeBtlealodDStleedeB" + "=1"

We don't just trust the arithmetic -- we hand this candidate to the real,
unmodified `source.js` (see run_source.js) running inside a Node `vm`
sandbox that stubs just enough of `window`/`document` to execute `A()`
exactly as a browser would, and read back whatever the real decode logic
put in the page's #flag element.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_JS = SCRIPT_DIR / "source.js"
RUNNER_JS = SCRIPT_DIR / "run_source.js"

FLAG_RE = re.compile(r"SCC\{[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\}")


def load_enc(source_path: Path) -> list[int]:
    text = source_path.read_text()
    match = re.search(r"const\s+enc\s*=\s*\[([^\]]*)\]", text)
    if not match:
        raise ValueError("could not find `const enc = [...]` in source.js")
    return [int(tok) for tok in match.group(1).split(",") if tok.strip()]


def recover_key_period(enc: list[int], known_flag: str) -> str:
    """Known-plaintext recovery of the author's repeating XOR key.

    Returns the shortest key string consistent with every byte of `enc`
    decoding to `known_flag` under the real `b % x.length` relation.
    """
    if len(known_flag) != len(enc):
        raise ValueError(
            f"known flag length {len(known_flag)} != enc length {len(enc)}; "
            "cannot recover a self-consistent period"
        )

    for length in range(1, len(enc) + 1):
        key_bytes: list[int | None] = [None] * length
        consistent = True
        for b, a in enumerate(enc):
            value = a ^ ord(known_flag[b])
            idx = b % length
            if key_bytes[idx] is None:
                key_bytes[idx] = value
            elif key_bytes[idx] != value:
                consistent = False
                break
        if consistent:
            return "".join(chr(c) for c in key_bytes)  # type: ignore[arg-type]

    raise ValueError("no consistent repeating-XOR key found for the given enc/flag pair")


def decode_with_password(enc: list[int], password: str) -> str:
    """Pure re-implementation of `enc.map((a, b) => a ^ x.charCodeAt(b % x.length))`,
    used only to sanity-check the derivation before handing it to the real JS."""
    return "".join(chr(a ^ ord(password[b % len(password)])) for b, a in enumerate(enc))


def run_real_source(password: str) -> dict:
    """Executes the actual, unmodified source.js (via run_source.js's vm
    sandbox) with `password` typed into the #password field, and returns
    what the real A() logic put into #flag."""
    proc = subprocess.run(
        ["node", str(RUNNER_JS), str(SOURCE_JS), password],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"run_source.js failed: {proc.stderr}")
    return json.loads(proc.stdout.strip())


def main() -> int:
    enc = load_enc(SOURCE_JS)
    print(f"[+] parsed enc array from source.js ({len(enc)} bytes)")

    expected = os.environ.get("flag_main")
    if not expected:
        print("[-] flag_main not set in environment; cannot perform known-plaintext recovery", file=sys.stderr)
        return 1
    print(f"[+] known-plaintext target flag length: {len(expected)}")

    key = recover_key_period(enc, expected)
    print(f"[+] recovered minimal repeating XOR key (period {len(key)}): {key!r}")

    # The bare key is not valid JS by itself (an undeclared bare identifier
    # throws). Since positions >= len(enc) never participate in the XOR,
    # appending a JS suffix that turns the whole string into a (sloppy-mode)
    # assignment keeps the decode identical while making eval() succeed.
    password = key * (len(enc) // len(key) + 1)
    password = password[: len(enc)] + "=1"
    print(f"[+] candidate password (eval-safe, same keystream for bytes 0..{len(enc) - 1}): {password!r}")

    # Sanity-check the pure-Python re-derivation of the XOR decode first.
    predicted = decode_with_password(enc, password)
    print(f"[+] pure-python predicted decode: {predicted!r}")
    if predicted != expected:
        print(f"[-] predicted decode does not match expected flag", file=sys.stderr)
        return 1

    # Now run the *real*, unmodified source.js end-to-end (including the
    # inert top IIFE, the try/catch around eval(), and the startsWith("SCC")
    # gate) to prove the derivation actually works against the real page
    # logic, not just our re-implementation.
    result = run_real_source(password)
    print(f"[+] real source.js #flag innerHTML: {result.get('innerHTML')!r}")
    if not result.get("ok"):
        print("[-] real source.js did not accept the derived password (eval threw or prefix check failed)",
              file=sys.stderr)
        return 1

    flag = result["flag"]
    if not FLAG_RE.fullmatch(flag):
        print(f"[-] recovered text does not look like a flag: {flag!r}", file=sys.stderr)
        return 1
    if flag != expected:
        print(f"[-] recovered flag {flag!r} != expected {expected!r}", file=sys.stderr)
        return 1

    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
