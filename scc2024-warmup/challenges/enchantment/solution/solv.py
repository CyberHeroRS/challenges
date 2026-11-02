#!/usr/bin/env python3
"""Solver for the "enchantment" challenge.

The player only receives a PDF rendered from `enchantment.tex`, which places
one glyph image per character using Minecraft's "Standard Galactic Alphabet"
(the Enchantment Table font). Each glyph image is named `char(NN).png`,
where NN is the ASCII code point of the letter it depicts - this is exactly
how `piton.py` (the original asset generator) produced them:

    for i in text:
        print('\\includegraphics{"./assets/char(' + str(ord(i)) + ').png"}')

So the *real* cipher key is simply: glyph image char(NN).png <-> chr(NN).
A human player has to recognize each Standard Galactic Alphabet glyph and
transcribe it back to a letter; here we reconstruct the same mapping by
reversing the generator's logic (ord(letter) -> filename) and reading the
exact sequence of glyphs laid out in enchantment.tex.
"""
import os
import re
import sys

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "challenge_assets")
TEX_PATH = os.path.join(ASSETS_DIR, "enchantment.tex")
IMAGES_DIR = os.path.join(ASSETS_DIR, "assets")

GRAPHIC_RE = re.compile(r'\\includegraphics\{"\./assets/char\((\d+)\)\.png"\}')


def decode_message() -> str:
    with open(TEX_PATH, "r", encoding="utf-8") as handle:
        tex = handle.read()

    codes = [int(match) for match in GRAPHIC_RE.findall(tex)]
    if not codes:
        raise RuntimeError("no glyph references found in enchantment.tex")

    message_chars = []
    for code in codes:
        glyph_path = os.path.join(IMAGES_DIR, f"char({code}).png")
        if not os.path.isfile(glyph_path):
            raise RuntimeError(f"missing glyph asset for code {code}: {glyph_path}")
        # Reverse the generator's mapping: filename ordinal -> original letter.
        message_chars.append(chr(code))

    return "".join(message_chars)


def extract_flag_body(message: str) -> str:
    # Message reads: WRAP.THE.FOLLOWING.TEXT.INTO.SCC.FLAG.FORMAT.<FLAG_BODY>
    tokens = message.split(".")
    if not tokens:
        raise RuntimeError("decoded message was empty")
    return tokens[-1]


def main() -> int:
    message = decode_message()
    flag_body = extract_flag_body(message)
    flag = f"SCC{{{flag_body}}}"

    print(f"Decoded message: {message}")
    print(f"Recovered flag: {flag}")

    expected = os.environ.get("flag_main")
    if expected is None:
        print("flag_main environment variable not set; cannot verify", file=sys.stderr)
        return 1

    if flag != expected:
        print(f"Flag mismatch: decoded={flag!r} expected={expected!r}", file=sys.stderr)
        return 1

    print("Flag verified successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
