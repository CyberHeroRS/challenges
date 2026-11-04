from pathlib import Path
import random

N = 256
LOG_N = 8
WORDS = 16
MASK64 = 0xFFFFFFFFFFFFFFFF
TEMPLATE_PATH = Path(__file__).resolve().parent / "src" / "generated_perm.template.cpp"

FLAG_BYTES = b"ju5s_P3rmut4te_th3_1Nput_Byt3s!!"
assert len(FLAG_BYTES) == 32


def route_benes(perm: list[int]) -> list[int]:
    n = len(perm)
    assert n >= 2 and (n & (n - 1)) == 0

    if n == 2:
        return [1] if perm[0] == 1 else [0]

    half = n // 2
    log_n = n.bit_length() - 1
    num_stages = 2 * log_n - 1
    masks = [0] * num_stages

    perm_inv = [0] * n
    for i, p in enumerate(perm):
        perm_inv[p] = i

    color = [-1] * n

    def color_path(start: int, c: int):
        node = start
        while color[node] == -1:
            color[node] = c
            dest = perm[node]
            partner_dest = dest ^ half
            node = perm_inv[partner_dest]
            c ^= 1

    for i in range(n):
        if color[i] == -1:
            color_path(i, 0)

    outer_mask = 0
    for i in range(half):
        if color[i] == 1:
            outer_mask |= 1 << i

    masks[0] = outer_mask
    masks[num_stages - 1] = outer_mask

    top_perm = [0] * half
    bot_perm = [0] * half

    for i in range(half):
        src_top = i if color[i] == 0 else i ^ half
        src_bot = i ^ half if color[i ^ half] == 1 else i
        dest_top = perm[src_top]
        dest_bot = perm[src_bot]
        top_perm[i] = dest_top if dest_top < half else dest_top ^ half
        bot_perm[i] = dest_bot if dest_bot < half else dest_bot ^ half

    top_masks = route_benes(top_perm)
    bot_masks = route_benes(bot_perm)

    for s, (tm, bm) in enumerate(zip(top_masks, bot_masks)):
        combined = 0
        for b in range(half):
            if (tm >> b) & 1:
                combined |= 1 << b
            if (bm >> b) & 1:
                combined |= 1 << (b + half)
        masks[s + 1] = combined

    return masks


def masks_to_stages(masks: list[int]) -> list[tuple[int, int]]:
    deltas = [1 << i for i in range(LOG_N)] + [1 << i for i in range(LOG_N - 2, -1, -1)]
    assert len(deltas) == len(masks) == 15
    return list(zip(masks, deltas))


def delta_swap_lane(x: int, mask: int, delta: int) -> int:
    t = ((x >> delta) ^ x) & mask
    return (x ^ t ^ (t << delta)) & MASK64


def cross_swap_lane(a: int, b: int, mask: int) -> tuple[int, int]:
    t = a & mask
    a = (a & ~mask) | (b & mask)
    b = (b & ~mask) | t
    return a & MASK64, b & MASK64


def apply_perm_stages_cpp_model(x: int, stages: list[tuple[int, int]]) -> int:
    lanes = split_lanes(x)
    for mask, delta in stages:
        w = split_mask(mask)
        if delta < 64:
            for i in range(4):
                lanes[i] = delta_swap_lane(lanes[i], w[i], delta)
        elif delta == 64:
            lanes[0], lanes[1] = cross_swap_lane(lanes[0], lanes[1], w[0])
            lanes[2], lanes[3] = cross_swap_lane(lanes[2], lanes[3], w[2])
        elif delta == 128:
            lanes[0], lanes[2] = cross_swap_lane(lanes[0], lanes[2], w[0])
            lanes[1], lanes[3] = cross_swap_lane(lanes[1], lanes[3], w[1])
        else:
            raise RuntimeError(f"unexpected Benes delta: {delta}")
    return join_lanes(lanes)


def split_mask(mask: int) -> list[int]:
    return [(mask >> (64 * i)) & MASK64 for i in range(4)]


def split_lanes(x: int) -> list[int]:
    return [(x >> (64 * i)) & MASK64 for i in range(4)]


def join_lanes(lanes: list[int]) -> int:
    out = 0
    for i, lane in enumerate(lanes):
        out |= (lane & MASK64) << (64 * i)
    return out


def emit_u64_mask_vec(name: str, lanes: list[int]) -> list[str]:
    return [
        f"  const auto {name} = make_u64x4("
        f"0x{lanes[0]:016X}ULL, 0x{lanes[1]:016X}ULL, "
        f"0x{lanes[2]:016X}ULL, 0x{lanes[3]:016X}ULL);"
    ]


def emit_perm_stage(i: int, mask: int, delta: int) -> list[str]:
    w = split_mask(mask)
    lines = [f"  // perm stage {i} delta={delta}"]
    mask_name = f"perm_mask_{i}"

    if delta < 64:
        lines += emit_u64_mask_vec(mask_name, [w[0], w[1], w[2], w[3]])
        lines.append(f"  s = delta_swap64<{delta}>(s, {mask_name});")
    elif delta == 64:
        lines += emit_u64_mask_vec(mask_name, [w[0], w[0], w[2], w[2]])
        lines.append(f"  s = cross_swap64(s, {mask_name});")
    elif delta == 128:
        lines += emit_u64_mask_vec(mask_name, [w[0], w[1], w[0], w[1]])
        lines.append(f"  s = cross_swap128(s, {mask_name});")
    else:
        raise RuntimeError("unexpected Benes delta")

    return lines


def emit_cpp_256(
    s: int,
    perm_stages: list[tuple[int, int]],
) -> str:
    perm_lines: list[str] = []
    lanes = split_lanes(s)
    for i, (mask, delta) in enumerate(perm_stages):
        perm_lines += emit_perm_stage(i, mask, delta)
        perm_lines.append("")

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    flag_placeholder = "{0}; /*__FLAG__*/"
    if flag_placeholder not in template_text:
        raise RuntimeError("Template FLAG placeholder not found")
    if "/*__PERM_STAGES__*/" not in template_text:
        raise RuntimeError("Template PERM_STAGES placeholder not found")

    rendered = template_text.replace(
        flag_placeholder,
        "{" + ", ".join(f"0x{lane:016X}ULL" for lane in lanes) + "};",
        1,
    ).replace("/*__PERM_STAGES__*/", "\n".join(perm_lines).rstrip(), 1)
    rendered += "\n"
    return rendered


if __name__ == "__main__":
    perm_rng = random.Random(0xDEADBEEF)
    perm = list(range(N))
    perm_rng.shuffle(perm)
    perm_masks = route_benes(perm)
    perm_stages = masks_to_stages(perm_masks)
    s = apply_perm_stages_cpp_model(int.from_bytes(FLAG_BYTES, "little"), perm_stages)

    print(emit_cpp_256(s, perm_stages))
