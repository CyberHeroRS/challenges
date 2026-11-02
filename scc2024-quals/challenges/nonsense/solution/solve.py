"""Solver for "nonsense".

The challenge performs a Diffie-Hellman-like key exchange inside the
rotation subgroup of SageMath's DihedralGroup(p) (p prime, 17 bits).
`g` is the generator used for `Dn.gens()[0]`, which SageMath always picks
as the pure rotation-by-1 permutation on the points {1, ..., p}, printed
in cycle notation as `(1,2,3,...,p)`.

Because that rotation subgroup is cyclic of (small, prime) order p, any
power `g**k` is itself a single p-cycle whose cycle notation starts
"(1, 1+k, 1+2k, ...)" (all values reduced into the 1..p range). That
means the secret exponents `a` and `b` -- and therefore the whole
discrete-log problem that Pohlig-Hellman would normally be needed for --
can be read directly off the *second* element of A's/B's printed cycle:
no brute force or generic DLP solver is required, the leaked permutation
representation already reveals the exponent mod p.

Once we know a mod p and b mod p, the shared secret `shared_a = A**b`
is again just `g**(a*b mod p)`, so we can reconstruct its exact cycle
string the same way SageMath would have printed it, hash it, and decrypt
the AES-ECB ciphertext to recover the flag.
"""
import ast
from hashlib import sha256

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def parse_assignment(line: str) -> str:
    return line.split("=", 1)[1].strip()


def parse_cycle(value: str) -> list[int]:
    assert value[0] == "(" and value[-1] == ")"
    return [int(tok) for tok in value[1:-1].split(",")]


def rotation_step(cycle: list[int], p: int) -> int:
    # cycle[0] == 1 always (DihedralGroup rotation subgroup element printed
    # starting from point 1); the next entry reveals the rotation amount.
    return (cycle[1] - cycle[0]) % p


def cycle_string(step: int, p: int) -> str:
    vals = []
    cur = 1
    for _ in range(p):
        vals.append(cur)
        cur = ((cur - 1 + step) % p) + 1
    return "(" + ",".join(str(v) for v in vals) + ")"


def main() -> None:
    with open("output.txt") as f:
        lines = f.read().splitlines()

    data = {}
    for line in lines:
        key = line.split("=", 1)[0].strip()
        data[key] = parse_assignment(line)

    p = int(data["p"])
    A = parse_cycle(data["A"])
    B = parse_cycle(data["B"])
    c = ast.literal_eval(data["c"])

    a = rotation_step(A, p)
    b = rotation_step(B, p)
    shared_step = (a * b) % p

    shared_str = cycle_string(shared_step, p)
    key = sha256(shared_str.encode()).digest()

    cipher = AES.new(key, AES.MODE_ECB)
    pt = unpad(cipher.decrypt(c), 16)
    print(pt.decode())


if __name__ == "__main__":
    main()
