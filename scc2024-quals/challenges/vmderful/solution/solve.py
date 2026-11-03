import os
import struct

# vmderful.exe is a custom bytecode VM (decompiled with ilspycmd) whose
# interpreter loop reads one opcode byte at a time from program.vm and
# dispatches to a handler class looked up by that opcode. Reversing the
# decompiled C# handler classes (Instr1..Instr28, corresponding to opcode
# bytes 0x00..0x1b) yields the following instruction set:
#
#   0x00 PUSH_FLAG            push the user-supplied candidate flag string
#   0x01 STR_LEN              pop str                 -> push int(len(str))
#   0x02 PUSH_BOOL   imm:u8                           -> push bool
#   0x03 PUSH_INT    imm:i32                          -> push int
#   0x04 PUSH_STR    imm:u8 len, len ASCII bytes       -> push str
#   0x05 DUP_BOOL              pop bool                -> push, push
#   0x06 DUP_INT               pop int                 -> push, push
#   0x07 DUP_STR               pop str                 -> push, push
#   0x08 SUBSTR      imm:i32 start, imm:i32 len; pop str -> push str.Substring
#   0x09 CONCAT                pop b, pop a            -> push a + b
#   0x0a CHAR_AT     imm:i32 idx; pop str              -> push int(str[idx])
#   0x0b INT_EQ                pop b, pop a            -> push a == b
#   0x0c INT_NEQ               pop b, pop a            -> push a != b
#   0x0d INT_GT                pop b, pop a            -> push a > b
#   0x0e INT_LT                pop b, pop a            -> push a < b
#   0x0f INT_GE                pop b, pop a            -> push a >= b
#   0x10 INT_LE                pop b, pop a            -> push a <= b
#   0x11 JMP         imm:i32 target                   -> unconditional jump
#   0x12 JMP_IF      imm:i32 target; pop bool          -> jump if true
#   0x13 ADD                   pop b, pop a            -> push a + b
#   0x14 SUB                   pop b, pop a            -> push a - b
#   0x15 XOR                   pop b, pop a            -> push a ^ b
#   0x16 MUL                   pop b, pop a            -> push a * b
#   0x17 DIV                   pop b, pop a            -> push a / b
#   0x18 LOAD_VAR    imm:i32 idx                       -> push var[idx]
#   0x19 STORE_VAR   imm:i32 idx; pop                  -> var[idx] = value
#   0x1a PRINT_STR             pop str                 -> print(str)
#   0x1b HALT                  jump straight to EOF (terminates the run loop)
#
# program.vm first checks len(flag) == 43, then runs 43 near-identical
# per-character blocks shaped exactly like tiny-vm's obfuscation:
#
#     PUSH_FLAG; CHAR_AT <i>            # temp = ord(flag[i])
#     PUSH_INT <c1>; <ADD|SUB|XOR>      # temp = temp OP c1
#     PUSH_INT <c2>; <ADD|SUB|XOR>      # temp = temp OP c2
#     ...
#     PUSH_INT <target>; INT_NEQ        # push (temp != target)
#     JMP_IF 5                          # jump to "Try Again!" if mismatched
#
# All three ops are invertible over 32-bit wraparound arithmetic (ADD/SUB are
# inverses of each other, XOR is self-inverse), so each character can be
# recovered directly from its block's constants and final target, without
# ever running the VM or brute forcing a byte.

OP_PUSH_FLAG = 0x00
OP_PUSH_BOOL = 0x02
OP_PUSH_INT = 0x03
OP_PUSH_STR = 0x04
OP_SUBSTR = 0x08
OP_CHAR_AT = 0x0A
OP_INT_NEQ = 0x0C
OP_JMP = 0x11
OP_JMP_IF = 0x12
OP_ADD = 0x13
OP_SUB = 0x14
OP_XOR = 0x15
OP_LOAD_VAR = 0x18
OP_STORE_VAR = 0x19

NAMES = {
    OP_PUSH_FLAG: "PUSH_FLAG",
    0x01: "STR_LEN",
    OP_PUSH_BOOL: "PUSH_BOOL",
    OP_PUSH_INT: "PUSH_INT",
    OP_PUSH_STR: "PUSH_STR",
    0x05: "DUP_BOOL",
    0x06: "DUP_INT",
    0x07: "DUP_STR",
    OP_SUBSTR: "SUBSTR",
    0x09: "CONCAT",
    OP_CHAR_AT: "CHAR_AT",
    0x0B: "INT_EQ",
    OP_INT_NEQ: "INT_NEQ",
    0x0D: "INT_GT",
    0x0E: "INT_LT",
    0x0F: "INT_GE",
    0x10: "INT_LE",
    OP_JMP: "JMP",
    OP_JMP_IF: "JMP_IF",
    OP_ADD: "ADD",
    OP_SUB: "SUB",
    OP_XOR: "XOR",
    0x16: "MUL",
    0x17: "DIV",
    OP_LOAD_VAR: "LOAD_VAR",
    OP_STORE_VAR: "STORE_VAR",
    0x1A: "PRINT_STR",
    0x1B: "HALT",
}

# opcodes that read a single i32 immediate right after the opcode byte
_I32_IMM_OPS = {OP_CHAR_AT, OP_JMP, OP_JMP_IF, OP_LOAD_VAR, OP_STORE_VAR, OP_PUSH_INT}


def load_program():
    with open("program.vm", "rb") as f:
        return f.read()


def disassemble(data):
    """Decode the full program.vm byte stream into (addr, name, operands)."""
    instrs = []
    i = 0
    n = len(data)
    while i < n:
        addr = i
        op = data[i]
        i += 1
        name = NAMES.get(op, f"UNK_{op:#x}")
        operands = []
        if op == OP_PUSH_BOOL:
            operands.append(bool(data[i]))
            i += 1
        elif op in _I32_IMM_OPS:
            operands.append(struct.unpack_from("<i", data, i)[0])
            i += 4
        elif op == OP_PUSH_STR:
            length = data[i]
            i += 1
            operands.append(data[i : i + length].decode("latin1"))
            i += length
        elif op == OP_SUBSTR:
            operands.append(struct.unpack_from("<i", data, i)[0])
            i += 4
            operands.append(struct.unpack_from("<i", data, i)[0])
            i += 4
        instrs.append((addr, name, operands))
    return instrs


def extract_char_blocks(instrs):
    """Split the instruction stream into the per-character check blocks.

    Each block is: CHAR_AT <idx>, (PUSH_INT <c>, ADD|SUB|XOR)*,
    PUSH_INT <target>, INT_NEQ, JMP_IF <fail_addr>.
    """
    blocks = {}
    i = 0
    n = len(instrs)
    while i < n:
        _, name, ops = instrs[i]
        if name != "CHAR_AT":
            i += 1
            continue
        idx = ops[0]
        i += 1
        chain = []
        target = None
        while True:
            _, op_name, op_ops = instrs[i]
            assert op_name == "PUSH_INT", f"expected PUSH_INT at {instrs[i]}"
            const = op_ops[0]
            _, next_name, _ = instrs[i + 1]
            if next_name in ("ADD", "SUB", "XOR"):
                chain.append((next_name, const))
                i += 2
                continue
            assert next_name == "INT_NEQ", f"expected INT_NEQ at {instrs[i + 1]}"
            target = const
            i += 2
            _, jmp_name, _ = instrs[i]
            assert jmp_name == "JMP_IF", f"expected JMP_IF at {instrs[i]}"
            i += 1
            break
        blocks[idx] = (chain, target)
    return blocks


def u32(x):
    return x & 0xFFFFFFFF


def reverse_char(chain, target):
    """Undo the ADD/SUB/XOR chain (all invertible mod 2**32) to recover the
    original character value from the final comparison target."""
    val = u32(target)
    for op, const in reversed(chain):
        c = u32(const)
        if op == "ADD":
            val = u32(val - c)
        elif op == "SUB":
            val = u32(val + c)
        elif op == "XOR":
            val = u32(val ^ c)
        else:
            raise ValueError(f"unknown op {op!r}")
    return val


def main():
    data = load_program()
    instrs = disassemble(data)
    blocks = extract_char_blocks(instrs)

    flag_chars = [None] * len(blocks)
    for idx, (chain, target) in blocks.items():
        flag_chars[idx] = reverse_char(chain, target)

    assert all(c is not None for c in flag_chars), "missing character block(s)"
    flag = "".join(chr(c) for c in flag_chars)
    print(flag)

    expected = os.environ.get("flag_main")
    if expected and expected not in flag:
        print(f"MISMATCH: expected substring {expected!r} not in decoded flag {flag!r}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
