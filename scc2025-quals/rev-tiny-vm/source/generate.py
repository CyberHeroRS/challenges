import random

def obfuscate_char(index, original_val, num_ops=200):
    ops = []
    ops.append(f"push {index}")
    ops.append("getChar")

    temp = original_val

    for _ in range(num_ops):
        op = random.choice(["add", "sub", "xor"])
        val = random.randint(100, 10000)
        ops.append(f"push {val}")
        ops.append(op)

        if op == "add":
            temp += val
        elif op == "sub":
            temp -= val
        elif op == "xor":
            temp ^= val

    ops.append(f"push {index}")
    ops.append("setChar")

    return ops, temp

def generate_challenge_py():
    original_flag = "SCC{vms_arent_so_hard!}"
    flag_ints = [ord(c) for c in original_flag]

    all_code = []
    final_result = []

    for i, val in enumerate(flag_ints):
        ops, result = obfuscate_char(i, val, num_ops=200)
        all_code.extend(ops)
        final_result.append(result)

    # Escape instructions as Python string list
    instruction_lines = ',\n        '.join(f'"{op}"' for op in all_code)
    result_list = ', '.join(str(v) for v in final_result)

    with open("challenge.py", "w") as f:
        f.write(f'''\
class VM:
    def __init__(self, flag):
        self.stack = []
        self.flag = [ord(c) for c in flag]
        self.pc = 0
        self.instructions = []
        self.halted = False

    def run(self, code):
        self.instructions = code
        self.pc = 0
        while self.pc < len(self.instructions) and not self.halted:
            self.execute(self.instructions[self.pc])
            self.pc += 1

    def execute(self, instr):
        parts = instr.split()
        op = parts[0]
        arg = int(parts[1]) if len(parts) > 1 else None

        if op == "push":
            self.stack.append(arg)
        elif op == "add":
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif op == "sub":
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif op == "xor":
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ^ b)
        elif op == "getChar":
            index = self.stack.pop()
            self.stack.append(self.flag[index])
        elif op == "setChar":
            index = self.stack.pop()
            value = self.stack.pop()
            self.flag[index] = value
        elif op == "ret":
            self.halted = True
        else:
            raise Exception(f"Unknown instruction: {{op}}")

def challenge():
    flag = input("Enter flag: ")

    if len(flag) != 24:
        print("[-] Flag must be exactly 24 characters long.")
        return

    vm = VM(flag)
    vm.run([
        {instruction_lines}
    ])

    if vm.flag == [{result_list}]:
        print("[+] Correct!")
    else:
        print("[-] Nop")

if __name__ == "__main__":
    challenge()
''')

    print("[+] challenge.py has been created!")

if __name__ == "__main__":
    generate_challenge_py()
