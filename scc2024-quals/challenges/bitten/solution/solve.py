#!/usr/bin/env python3
"""Solver for the "bitten" challenge.

The generator encodes each flag bit ``b`` as ``g ** (b + rp) mod p`` where
``rp`` is a fresh random 256-bit prime and the Jacobi symbol of ``g`` with
respect to ``p`` is -1.

Since every 256-bit prime ``rp`` (other than 2, which never occurs at this
size) is odd, ``jacobi(g, p) ** rp == -1``. Jacobi symbols are multiplicative
over modular exponentiation, so:

    jacobi(g**(b+rp) mod p, p) == jacobi(g, p)**(b+rp)
                                == (-1)**b * (-1)**rp
                                == (-1)**b * -1

That means an output's Jacobi symbol is -1 when the encoded bit was 0, and
+1 when the encoded bit was 1 - independent of the random prime used to mask
the exponent. Recovering every bit this way reconstructs the flag.
"""

import ast
from pathlib import Path

from sympy import jacobi_symbol

OUTPUT_PATH = Path(__file__).parent / "output.txt"


def load_output(path: Path) -> tuple[int, int, list[int]]:
    lines = path.read_text().splitlines()
    g = int(lines[0].split("=", 1)[1])
    p = int(lines[1].split("=", 1)[1])
    outs = ast.literal_eval(lines[2])
    return g, p, outs


def recover_flag(g: int, p: int, outs: list[int]) -> str:
    assert jacobi_symbol(g, p) == -1, "expected jacobi(g, p) == -1"

    bits = "".join("1" if jacobi_symbol(o, p) == 1 else "0" for o in outs)

    flag_bytes = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]
        flag_bytes.append(int(byte, 2))

    return flag_bytes.decode()


def main() -> None:
    g, p, outs = load_output(OUTPUT_PATH)
    flag = recover_flag(g, p, outs)
    print(flag)


if __name__ == "__main__":
    main()
