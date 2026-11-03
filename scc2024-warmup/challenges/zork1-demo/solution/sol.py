import os

from pwn import *

# The "unbeatable" goblin stores its HP in a single SIGNED byte.
# Choice 1 (attack) is the only move that damages it, but the goblin always
# hits back harder (19 dmg) than the player can deal (16 dmg), so straight
# attacking is provably unwinnable: 6 attacks (96 dmg) are required to bring
# a 90 HP goblin to <=0, but that costs 6*19=114 dmg to the player's 80 HP.
#
# The real bug: choice 4 ("take attack and recover") is the only way to gain
# mana (0 -> 1), and choice 3 ("scream") - when mana is available - instead
# of damaging the player, HEALS the goblin by 10 (unsigned byte add) and
# costs no player HP that round. Four scream heals push the goblin's stored
# byte from 90 to 130, which overflows the SIGNED byte check used to decide
# whether the fight is still going (`test al,al; jg`), making 130 (0x82)
# read as -126 -- i.e. "defeated". Alternating 4,3 four times costs only
# 4*19=76 HP (player survives at 4 HP) while "healing" the goblin into a
# win condition. Afterwards, picking up the golden tooth sets the flag bit
# the king() routine checks before printing the flag.

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

p.sendlineafter(b"> ", b"read leaflet")

for _ in range(4):
    p.sendlineafter(b"> ", b"4")  # take attack and recover -> gain 1 mana
    p.sendlineafter(b"> ", b"3")  # scream -> heals goblin, overflows its HP byte negative

p.sendlineafter(b"> ", b"pickup the golden tooth")

print(p.recvall(timeout=15).decode(errors="replace"))
