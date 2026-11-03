#!/usr/local/bin/python

import os
import re
from Crypto.Util.number import *
import time
import random

# The LCG seed is this challenge's own "whack-a-mole-2" flag: recovering it
# from the leaked states is that variant's win condition. It does NOT need
# to match the real deployed flag for THIS ("whack-a-mole-1") deployment to
# work correctly -- only whack-a-mole-2's deployment sets SEED_FLAG (via
# challenge.yaml's env-based flag injection); this one falls back to a
# fixed placeholder so the LCG still has a valid integer to seed from.
_seed_flag = os.environ.get("SEED_FLAG", "")
_seed_match = re.search(r"\d+", _seed_flag)
seed = int(_seed_match.group()) if _seed_match else 202420242024202420242024

# This challenge's own ("whack-a-mole-1") flag, printed verbatim after a
# win; injected via challenge.yaml's env-based flag mechanism (already
# wrapped in the event's flag format, e.g. "SCC{...}").
FLAG = os.environ.get("FLAG", "SCC{placeholder_flag_not_set}")

# nije deo zadatka, samo crtezi krtica
krtica_banner = "\n\n["+" "*21+"/===\\"+" "*29+"]\n["+" "*20+"/o  o \\"+" "*28+"]\n["+" " * \
    19+"/ ----  \\"+" "*27 + \
    "]\n[     _____ ...     ---------   _____   _____ ... _____ ]\n\n"
win_banner = "[  TACNO!!"+" "*14+",\n["+" "*22+"/(  ___________\n["+" "*21+"|  >:===========`\n["+" "*22+")(\n["+" "*22+"\"\"\n["+" "*20+"/===\\" + \
    " "*29+"]\n["+" "*19+"/x  x \\"+" "*28+"]\n["+" "*18+"/   o   \\" + \
    " "*27+"]\n[    _____ ...     ---------   _____   _____ ... _____ ]\n"
fail_banner = "[  NETACNO :p"+" "*11+"\n["+" "*40+",\n["+" "*21+"/===\\"+" "*13 + \
    "/(  __________  ]\n["+" "*20+"/ ^  ^\\"+" "*11+"|  >:==========1 ]\n["+" "*19 + \
    "/    U  \\           )("+" "*14 + \
                           "]\n[     _____ ...     ---------   _____   \"\" ... _____    ]\n"

# klasa koja implementira osnovni oblik LCG


class LCG():
    def __init__(self, seed):
        self.seed = seed
        self.a = getPrime(self.seed.bit_length())
        self.c = getPrime(self.seed.bit_length())
        self.m = getPrime(self.seed.bit_length() + 1)
        # print("[+]DEBUG: seed:", self.seed, "\n{+}DEBUG: a:", self.a, "\n[+]DEBUG: c:", self.c, "\n[+]DEBUG: mod:", self.m, "\n")

    def next(self):
        self.seed = ((self.seed * self.a) + self.c) % self.m
        # print("[+]DEBUG: novo stanje izracunato:", self.seed)
        return self.seed


# glavni deo zadatka
l = LCG(seed)
s1 = l.next()
s2 = l.next()
s3 = l.next()


print("  [-] Dobro dosli u poznatu igru na vasarima, \"istrebite krtice iz dvorista\"")
time.sleep(500/1000)
print(f"     U dvoristu postoji {l.m} rupa, koje su napravile 5 krtica")
time.sleep(500/1000)
print("     Dajte sve od sebe da pobedite svih 5 krtica!")
print(krtica_banner)

# dostavljanje korisniku potrebnih informacija
print("\ntri stanja:", s1, s2, s3)

# proveravanje korisnickog inputa
for i in range(5):
    s4 = l.next()
    print(f"Koji broj rupe zelite da udarite cekicem? (0 - {l.m})")
    usr = input()
    if (int(usr) == s4):
        print(win_banner)
    else:
        print(fail_banner)
        quit()

print(f"ZASTAVA1: {FLAG}")

