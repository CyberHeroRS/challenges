#!/usr/bin/env python3

import argparse
import hashlib

from elftools.elf.elffile import ELFFile


def main() -> int:
    parser = argparse.ArgumentParser(description="SHA-256 of ELF .text section")
    parser.add_argument("binary", nargs="?", default="builddir/chall")
    args = parser.parse_args()

    with open(args.binary, "rb") as f:
        elf = ELFFile(f)
        text = elf.get_section_by_name(".text")
        if text is None:
            raise SystemExit("error: .text section not found")
        hash = hashlib.sha256(text.data()).digest()
        print(hash.hex())
        print("{ "+ ", ".join(f"0x{b:02x}" for b in hash) + " }")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
