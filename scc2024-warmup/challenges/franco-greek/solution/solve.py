#!/usr/bin/env python3
"""Solver for the "Franco-Greek" classical-cipher challenge.

The cipher ("Franco-Greek machine") is two classical techniques stacked together:

1. "Greek" layer - a fixed monoalphabetic substitution where each of the 26
   English letters is disguised as a visually similar ("homoglyph") character
   drawn from Greek, Cyrillic, Hebrew, math and Latin Unicode blocks (e.g. the
   Greek letter "rho" stands in for "p", Cyrillic "ya" for a mirrored "r", the
   partial-differential sign for "d", etc). Spaces and punctuation are left
   untouched.
2. "Franco" layer - a classic Vigenere cipher (invented by the Frenchman
   Blaise de Vigenere) applied on top, using the repeating key "SAFEKEY". Only
   letter positions advance the running key; punctuation/spaces are skipped.

Decoding therefore undoes the Vigenere shift first (per letter, using the
repeating key) and then maps the recovered intermediate letter back through
the homoglyph table to get the plaintext letter.
"""

from __future__ import annotations

import string
from pathlib import Path

ENCODED_PATH = Path(__file__).parent / "encoded.txt"

# The 26 homoglyph code points used by the cipher, each mapped to the plain
# English letter it visually disguises. Code points (not literal characters)
# are used here to avoid any ambiguity between precomposed and decomposed
# Unicode forms.
GLYPH_TO_LETTER = {
    0x2113: "l",  # SCRIPT SMALL L
    0x0443: "y",  # CYRILLIC SMALL LETTER U
    0x044F: "r",  # CYRILLIC SMALL LETTER YA (mirrored R)
    0x03B9: "i",  # GREEK SMALL LETTER IOTA
    0x0455: "s",  # CYRILLIC SMALL LETTER DZE
    0x0066: "f",  # LATIN SMALL LETTER F
    0x03BD: "v",  # GREEK SMALL LETTER NU
    0x03B1: "a",  # GREEK SMALL LETTER ALPHA
    0x043D: "h",  # CYRILLIC SMALL LETTER EN
    0x03C1: "p",  # GREEK SMALL LETTER RHO
    0x0067: "g",  # LATIN SMALL LETTER G
    0x043A: "k",  # CYRILLIC SMALL LETTER KA
    0x03C3: "o",  # GREEK SMALL LETTER SIGMA
    0x0442: "t",  # CYRILLIC SMALL LETTER TE
    0x03C5: "u",  # GREEK SMALL LETTER UPSILON
    0x0432: "b",  # CYRILLIC SMALL LETTER VE
    0x0438: "n",  # CYRILLIC SMALL LETTER I (mirrored N)
    0x007A: "z",  # LATIN SMALL LETTER Z
    0x05E3: "q",  # HEBREW LETTER FINAL PE
    0x03C2: "c",  # GREEK SMALL LETTER FINAL SIGMA
    0x0454: "e",  # CYRILLIC SMALL LETTER UKRAINIAN IE
    0x03C9: "w",  # GREEK SMALL LETTER OMEGA
    0x043C: "m",  # CYRILLIC SMALL LETTER EM
    0x2202: "d",  # PARTIAL DIFFERENTIAL SIGN
    0xFB2F: "x",  # HEBREW LETTER ALEF WITH QAMATS
    0x05E0: "j",  # HEBREW LETTER NUN
}

VIGENERE_KEY = "safekey"
PASSTHROUGH = set(" ,.:_{}")


def vigenere_decrypt_letter(letter: str, key_letter: str) -> str:
    shift = string.ascii_lowercase.index(key_letter)
    value = string.ascii_lowercase.index(letter)
    return string.ascii_lowercase[(value - shift) % 26]


def decode(ciphertext: str) -> str:
    out = []
    key_index = 0
    for ch in ciphertext:
        if ch in PASSTHROUGH or ch == "\n":
            out.append(ch)
            continue
        intermediate = GLYPH_TO_LETTER.get(ord(ch))
        if intermediate is None:
            raise ValueError(f"unknown cipher glyph: {ch!r} (U+{ord(ch):04X})")
        key_letter = VIGENERE_KEY[key_index % len(VIGENERE_KEY)]
        out.append(vigenere_decrypt_letter(intermediate, key_letter))
        key_index += 1
    return "".join(out)


def main() -> None:
    ciphertext = ENCODED_PATH.read_text(encoding="utf-8")
    plaintext = decode(ciphertext)
    print(plaintext)

    marker = "flag: "
    start = plaintext.index(marker) + len(marker)
    flag_body = plaintext[start:].strip()
    # The decoded text already spells the flag verbatim as "scc{...}"; only
    # the challenge-prefix convention ("SCC") needs upper-casing to match the
    # platform's flag format.
    flag = "SCC" + flag_body[3:]
    print(flag)


if __name__ == "__main__":
    main()
