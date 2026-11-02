"""
Solver for "Weaponized Key".

The obfuscation in SecretWeapon.ps1 is pure PowerShell variable-name
scrambling: every meaningful name (and even the helper function/parameter
names) is replaced with a long random identifier, but the *structure* of
the script is untouched. Comparing SecretWeapon.ps1 with SecretWeaponRaw.ps1
(the de-obfuscated/annotated reference the attacker apparently also had)
shows the real logic:

  1. Twelve variables each hold one small Base64 fragment of a secret key,
     e.g. $D1g1t = "bDM0".
  2. Four "Part" variables concatenate three fragments each with the `+`
     operator (the trailing `-join ''` is a no-op here, since joining a
     single already-concatenated string changes nothing - pure obfuscation
     flavor):
         $Part1 = $D1g1t + $Extr4 + $End -join ''
  3. The four Part variables are joined, *out of numeric order*
     (Part3, Part4, Part2, Part1), into one Base64 string ($K3yV4lu3).
  4. That Base64 string is decoded and appended to a base URL - but the
     decoded bytes are already the flag, because the challenge "secret
     key" the obfuscated malware fetches remotely *is* the flag.

Rather than hardcoding the recovered value, this script re-implements that
exact pipeline in Python by parsing the real (still-obfuscated)
SecretWeapon.ps1 structurally - it never relies on the human-friendly
variable names from the Raw reference file, only on the shape of the
PowerShell statements, so it works against the actual obfuscated artifact.
"""

import base64
import pathlib
import re

SCRIPT_PATH = pathlib.Path(__file__).parent / "SecretWeapon.ps1"

# $VarName = "literal string"
LITERAL_RE = re.compile(r'^\$(\w+)\s*=\s*"([^"]*)"\s*$')

# $VarName = $a + $b + ... + $z -join ''
CONCAT_RE = re.compile(
    r"^\$(\w+)\s*=\s*((?:\$\w+\s*\+\s*)+\$\w+)\s*-join\s*''\s*$"
)

# $VarName = ($a, $b, ... , $z) -join ''
LIST_JOIN_RE = re.compile(
    r"^\$(\w+)\s*=\s*\(([^()]*)\)\s*-join\s*''\s*$"
)

VAR_REF_RE = re.compile(r"\$(\w+)")


def resolve(values, name):
    if name not in values:
        raise KeyError(f"Unresolved PowerShell variable: ${name}")
    return values[name]


def main():
    text = SCRIPT_PATH.read_text()

    values = {}
    key_value_b64 = None

    for line in text.splitlines():
        line = line.strip()

        m = LITERAL_RE.match(line)
        if m:
            name, literal = m.groups()
            values[name] = literal
            continue

        m = CONCAT_RE.match(line)
        if m:
            name, expr = m.groups()
            refs = VAR_REF_RE.findall(expr)
            values[name] = "".join(resolve(values, r) for r in refs)
            continue

        m = LIST_JOIN_RE.match(line)
        if m:
            name, inner = m.groups()
            refs = VAR_REF_RE.findall(inner)
            joined = "".join(resolve(values, r) for r in refs)
            values[name] = joined
            # This is the "secret key" build-up step in the script
            # (assigned right before it is Base64-decoded and used to
            # build the callback URL). Remember it as our candidate.
            key_value_b64 = joined
            continue

    if key_value_b64 is None:
        raise SystemExit("Could not locate the Base64 key-building statement")

    decoded = base64.b64decode(key_value_b64).decode()
    print(f"Reconstructed secret key (Base64): {key_value_b64}")
    print(f"Decoded secret key: {decoded}")

    flag_match = re.search(r"SCC\{[^}]*\}", decoded)
    if not flag_match:
        raise SystemExit(f"Decoded value did not contain a flag: {decoded!r}")

    print(f"Flag: {flag_match.group(0)}")


if __name__ == "__main__":
    main()
