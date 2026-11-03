"""
Solver for ClickerGame (scc2024-quals).

The APK embeds a hex-encoded, XOR-"encrypted" flag string as an Android
string resource inside resources.arsc. The XOR keystream is produced by
java.util.Random seeded with 322419390L, after "burning" 322419390
nextInt() calls (decompiled from classes.dex: MainActivity.onCreate calls
rnd.setSeed(322419390L); MainActivity.OnButtonClick calls rnd.nextInt()
once per click before checking whether the click counter has reached
322419390, at which point it starts XOR-ing resource bytes with
rnd.nextInt() & 0xFF per byte).

Since burning ~322 million calls one-by-one in Python would be slow, we
use the standard LCG "jump-ahead" trick: java.util.Random's internal
state update seed' = (seed * 0x5DEECE66D + 0xB) mod 2**48 is an affine
map, so N repeated applications can be collapsed into a single
(mult, add) pair via fast doubling/modular exponentiation, computed in
O(log N) instead of O(N). This is verified against a slow, literal loop
for small N in the self-check below before being trusted for the full
322,419,390-step jump.
"""

import re
import zipfile

APK_PATH = "/solution/clicker_game.apk"

SEED = 322419390
BURN_STEPS = 322419390

MASK48 = (1 << 48) - 1
MULT = 0x5DEECE66D
ADD = 0xB


def java_random_set_seed(seed: int) -> int:
    """Mirrors java.util.Random.setSeed(long)."""
    return (seed ^ MULT) & MASK48


def java_random_next_int(state: int) -> tuple[int, int]:
    """Mirrors one java.util.Random.next(32)/nextInt() step.

    Returns (new_state, signed_32_bit_value).
    """
    state = (state * MULT + ADD) & MASK48
    value = state >> 16  # next(bits) returns (int)(seed >>> (48 - bits)); bits=32
    if value >= (1 << 31):
        value -= 1 << 32
    return state, value


def jump_ahead(state: int, steps: int) -> int:
    """Advance the LCG state by `steps` applications in O(log steps) time.

    seed_{k+1} = (seed_k * MULT + ADD) mod 2**48 is an affine recurrence;
    repeated application composes via (mult, add) pairs that can be
    combined with fast doubling, analogous to matrix exponentiation.
    """
    cur_mult, cur_add = MULT, ADD
    acc_mult, acc_add = 1, 0
    remaining = steps
    while remaining > 0:
        if remaining & 1:
            acc_mult = (acc_mult * cur_mult) & MASK48
            acc_add = (acc_add * cur_mult + cur_add) & MASK48
        cur_add = (cur_add * (cur_mult + 1)) & MASK48
        cur_mult = (cur_mult * cur_mult) & MASK48
        remaining >>= 1
    return (state * acc_mult + acc_add) & MASK48


def self_check() -> None:
    """Verify jump_ahead against a slow, literal loop for small N."""
    import random as pyrandom

    for _ in range(5):
        state0 = java_random_set_seed(pyrandom.randint(0, 2**63))
        n = pyrandom.randint(0, 5000)

        slow_state = state0
        for _ in range(n):
            slow_state, _ = java_random_next_int(slow_state)

        fast_state = jump_ahead(state0, n)
        assert slow_state == fast_state, (
            f"jump-ahead mismatch for n={n}: slow={slow_state} fast={fast_state}"
        )


def extract_hex_flag_string(apk_path: str) -> str:
    """Scan the APK's resources.arsc for the embedded hex-encoded flag.

    The flag is stored as a plain Android string resource; its UTF-8 bytes
    show up verbatim as a long contiguous run of ASCII hex digits in the
    raw resources.arsc bytes, so we don't need a full resource-table
    parser - a regex scan over the raw bytes is sufficient and avoids
    hardcoding anything extracted from the APK itself.
    """
    with zipfile.ZipFile(apk_path) as zf:
        data = zf.read("resources.arsc")

    candidates = sorted(set(re.findall(rb"[0-9a-fA-F]{40,}", data)), key=len, reverse=True)
    if not candidates:
        raise RuntimeError("no hex-digit run found in resources.arsc")

    hex_bytes = candidates[0]
    if len(hex_bytes) % 2 != 0:
        raise RuntimeError("extracted hex string has odd length")

    return hex_bytes.decode("ascii")


def main() -> None:
    self_check()

    hex_flag = extract_hex_flag_string(APK_PATH)
    encrypted = bytes.fromhex(hex_flag)

    state = java_random_set_seed(SEED)
    state = jump_ahead(state, BURN_STEPS)

    out = bytearray(len(encrypted))
    for i, byte in enumerate(encrypted):
        state, value = java_random_next_int(state)
        out[i] = byte ^ (value & 0xFF)

    flag = out.decode("utf-8")
    print(flag)


if __name__ == "__main__":
    main()
