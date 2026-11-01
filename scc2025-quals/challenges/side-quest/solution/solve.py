from pwn import *
import subprocess
import string

context.log_level='warn'

perf = "perf" #"/usr/lib/linux-tools/5.15.0-134-generic/perf"
binary = "../public/side-quest" 
charset = string.ascii_letters + string.digits + "{}_"
flag_length = 61
flag = ["?"] * flag_length
num_samples = 3

def measure_instructions(passphrase, runs=num_samples):
    return min(measure_instructions_proc(passphrase) for _ in range(runs))

def measure_instructions_proc(passphrase):
    cmd = f"{perf} stat -e instructions {binary}"
    p = process(cmd, shell=True)
    p.recvuntil(b"What would you like to do?")
    p.sendline(b"3")
    p.recvuntil(b"Passphrase:")
    p.sendline(passphrase.encode())
    p.sendline(b"4")
    output = p.recvall(timeout=1).decode(errors="ignore")
    p.close()
    for line in output.split("\n"):
        if "instructions" in line:
            try:
                return int(line.split()[0].replace(",", ""))
            except ValueError:
                return 0
    return -1

for i in range(flag_length):
    best_char = "?"
    best_instructions = 0

    for c in charset:
        test_flag = "".join(flag[:i]) + c + "?" * (flag_length - i - 1)
        instructions = measure_instructions(test_flag)

        print(test_flag, instructions)

        if instructions > best_instructions:
            best_instructions = instructions
            best_char = c

    flag[i] = best_char
    print(f"Current flag progress: {''.join(flag)}")

print(f"Final flag: {''.join(flag)}")