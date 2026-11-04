#!/usr/bin/env python3

import re
from pathlib import Path


def parse_array(src: str, name: str) -> bytes:
    m = re.search(rf"{name}\[\]\s*=\s*\{{([^}}]+)\}};", src)
    if not m:
        raise ValueError(f"Could not find array: {name}")
    nums = [int(x.strip(), 16) for x in m.group(1).split(",") if x.strip()]
    return bytes(nums)


def untransform_byte(v: int, k: int, i: int) -> int:
    v ^= 0xA7
    v = ((v >> 1) | ((v & 1) << 7)) & 0xFF
    return ((v - 0x35 + (i * 5)) & 0xFF) ^ k


def main() -> None:
    src = Path("main_compile.c").read_text(encoding="utf-8")
    enc = parse_array(src, "ENC_FLAG")
    key = parse_array(src, "KEY")

    flag = bytes(untransform_byte(enc[i], key[i], i) for i in range(len(enc)))
    print(flag.decode("utf-8"))


if __name__ == "__main__":
    main()
