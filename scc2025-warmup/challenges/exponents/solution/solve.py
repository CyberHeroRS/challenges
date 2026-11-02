"""
Exponents - exponent-manipulation attack.

The challenge publishes (with e = 3, d = e^-1 mod phi(n)):
    hint = d^e mod phi(n)       (i.e. hint = d^3 mod phi)
    enc  = m^e  mod n           (i.e. enc  = m^3 mod n, the RSA-encrypted flag)
    n    = p * q

Since e*d == 1 (mod phi), squaring gives (e*d)^2 == 1 (mod phi), i.e.
9*d^2 == 1 (mod phi). We never need p, q, phi or d explicitly - we can
reach the same exponent purely through modular exponentiation mod n:

    enc^hint mod n = (m^e)^(d^e) mod n = m^(e * d^e) mod n
                    = m^(3 * d^3) mod n = m^(d^2) mod n   (since 3*d == 1 mod phi)

    (enc^hint)^9 mod n = m^(9 * d^2) mod n = m^1 mod n = m   (since 9*d^2 == 1 mod phi)

So the flag is simply pow(pow(enc, hint, n), 9, n).
"""

from pathlib import Path


def parse_out(path: Path) -> dict:
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = int(val.strip())
    return values


def main() -> None:
    values = parse_out(Path("public/out.txt"))
    hint, enc, n = values["hint"], values["enc"], values["n"]

    step1 = pow(enc, hint, n)
    m = pow(step1, 9, n)

    flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
    print(flag.decode())


if __name__ == "__main__":
    main()
