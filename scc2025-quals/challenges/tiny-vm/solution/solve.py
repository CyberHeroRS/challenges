import os
import re

# tiny-vm bakes a per-character obfuscation program directly into the
# published source as a flat instruction list. For each flag character at
# index i, the VM does:
#     push i; getChar            # temp = original_val
#     push V1; <add|sub|xor>     # temp = temp OP V1
#     push V2; <add|sub|xor>     # temp = temp OP V2
#     ...
#     push i; setChar            # flag[i] = temp
# and the script then checks `vm.flag == [r0, r1, ..., r23]` (the final
# comparison list). Every operation (add/sub/xor) is invertible, so we can
# decode each character by reading its instruction block straight out of the
# VM program and replaying it backwards from the known final result:
#   - undo "add V" with "subtract V"
#   - undo "sub V" with "add V"
#   - undo "xor V" with "xor V" (self-inverse)


def load_source():
    with open("tiny-vm.py") as f:
        return f.read()


def extract_instructions(src):
    # vm.run([ "push 0", "getChar", ... ])
    m = re.search(r"vm\.run\(\[(.*?)\]\)", src, re.S)
    assert m, "could not find vm.run([...]) instruction list"
    body = m.group(1)
    return [s for s in re.findall(r'"([^"]*)"', body)]


def extract_final_result(src):
    # if vm.flag == [v0, v1, ...]:
    m = re.search(r"vm\.flag == \[([^\]]*)\]", src)
    assert m, "could not find final comparison list"
    return [int(x.strip()) for x in m.group(1).split(",")]


def split_per_char_blocks(instructions):
    """Split the flat instruction stream into per-character blocks, each
    delimited by "push <i>", "getChar" ... "push <i>", "setChar"."""
    blocks = {}
    i = 0
    n = len(instructions)
    while i < n:
        assert instructions[i].startswith("push ")
        idx = int(instructions[i].split()[1])
        assert instructions[i + 1] == "getChar"
        i += 2
        ops = []
        while not (
            instructions[i].startswith("push ")
            and i + 1 < n
            and instructions[i + 1] == "setChar"
        ):
            op = instructions[i]
            if op.startswith("push "):
                val = int(op.split()[1])
                arith = instructions[i + 1]
                ops.append((arith, val))
                i += 2
            else:
                raise Exception(f"unexpected instruction {op!r}")
        # instructions[i] == "push <idx>", instructions[i+1] == "setChar"
        i += 2
        blocks[idx] = ops
    return blocks


def reverse_char(ops, result):
    temp = result
    for op, val in reversed(ops):
        if op == "add":
            temp -= val
        elif op == "sub":
            temp += val
        elif op == "xor":
            temp ^= val
        else:
            raise Exception(f"unknown op {op!r}")
    return temp


def main():
    src = load_source()
    instructions = extract_instructions(src)
    final_result = extract_final_result(src)
    blocks = split_per_char_blocks(instructions)

    assert len(blocks) == len(final_result), (
        f"expected {len(final_result)} char blocks, found {len(blocks)}"
    )

    flag_chars = [None] * len(final_result)
    for idx, ops in blocks.items():
        flag_chars[idx] = reverse_char(ops, final_result[idx])

    flag = "".join(chr(c) for c in flag_chars)
    print(flag)

    expected = os.environ.get("flag_main")
    if expected and expected not in flag:
        print(f"MISMATCH: expected substring {expected!r} not in decoded flag {flag!r}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
