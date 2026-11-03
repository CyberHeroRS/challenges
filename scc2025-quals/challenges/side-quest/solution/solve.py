import hashlib
import os
import re
import string

# side-quest's "side channel" is really a stronger primitive hiding in plain
# sight: source/src/main.rs's check_passphrase() builds the passphrase
# prefix up to each index, reverses it, SHA-256-hashes it, and compares
# against a per-position commitment in a HASHES[] table. Since every prefix
# commits only to characters already fixed by prior rounds, each character
# can be recovered independently via brute force over a small charset,
# without ever running the live binary or measuring any timing/instruction
# side channel.

SRC_PATH = "/solution/main.rs"
CHARSET = string.ascii_letters + string.digits + "{}_"


def extract_hashes(src):
    m = re.search(r"const HASHES: \[&str; \d+\] = \[(.*?)\];", src, re.S)
    assert m, "could not find HASHES table in source"
    return re.findall(r'"([0-9a-f]{64,})"', m.group(1))


def main():
    with open(SRC_PATH) as f:
        src = f.read()
    hashes = extract_hashes(src)

    flag = ""
    for i, target in enumerate(hashes):
        found = None
        for c in CHARSET:
            candidate = flag + c
            check = candidate[::-1]
            digest = hashlib.sha256(check.encode()).hexdigest()
            if digest == target:
                found = c
                break
        if found is None:
            raise SystemExit(f"no charset character matched hash at index {i}")
        flag += found
        print(f"progress: {flag}")

    print(flag)

    expected = os.environ.get("flag_main")
    if expected and expected not in flag:
        print(f"MISMATCH: expected substring {expected!r} not in decoded flag {flag!r}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
