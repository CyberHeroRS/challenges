import os
import random

from pwn import context, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_HADES_III_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_HADES_III_SHELL_PORT", "1337"))

# A left-or-right-handed "guess which soul is the true random oracle"
# game, played 20 times (souls) using a shared pool of only 20 questions
# total. Each round assigns two NextGenPRF instances: one option=0
# (uniformly random in [0, p)), one option=1 (deterministic
# g^(AES(m1)^2 * AES(m2)) mod p, same AES key reused all game).
#
# Distinguisher: g=17's multiplicative order mod p is exactly (p-1)/4
# (verified by factoring p-1 and testing each prime-power cofactor), so
# <g> is an index-4 subgroup of Z_p*. ANY pseudorandom output is, by
# construction, some power of g and therefore ALWAYS satisfies
# x**((p-1)//4) == 1 (mod p) -- a guaranteed-true membership test. A
# genuinely uniform random value only lands in that same subgroup with
# probability ~1/4, so roughly 3 times out of 4 the true-random side's
# response visibly FAILS the test, letting us identify it with
# certainty from a single query (ask once per round, press the door for
# whichever side failed). When both sides happen to pass (the ~25% case
# where true-random coincidentally fell inside the subgroup too), there
# is no signal left to disambiguate within our question budget, so we
# just guess 50/50.
#
# A single game therefore only succeeds with a certain probability (not
# ~100%) -- failing any round ends the whole connection immediately, so
# this reconnects and replays the full 20-round game repeatedly until a
# connection wins outright.

p_mod = 8056155217297667024640676103489388132749565410810114417324337594619262050521095735634369412853881198743766882674233588531999412443768385413663901114403961
m_exp = (p_mod - 1) // 4


def is_member(x):
    return pow(x, m_exp, p_mod) == 1


def solve_once():
    conn = remote(HOST, PORT, timeout=15)
    conn.recvuntil(b"> ", timeout=15)
    for soul in range(20):
        conn.sendline(b"3")
        conn.recvuntil(b"question for the souls: ", timeout=15)
        msg = os.urandom(32)
        conn.sendline(msg.hex().encode())
        line1 = conn.recvline(timeout=15).decode()
        line2 = conn.recvline(timeout=15).decode()
        left_val = int(line1.split(":")[1].strip())
        right_val = int(line2.split(":")[1].strip())
        conn.recvuntil(b"> ", timeout=15)

        left_is_member = is_member(left_val)
        right_is_member = is_member(right_val)

        if left_is_member and not right_is_member:
            # right failed the membership test -> right is definitely
            # true_random -> press door 2.
            door = b"2"
        elif right_is_member and not left_is_member:
            # left failed the membership test -> left is definitely
            # true_random -> press door 1.
            door = b"1"
        else:
            door = random.choice([b"1", b"2"])

        conn.sendline(door)
        conn.recvline(timeout=15)  # leading blank line
        out = conn.recvline(timeout=15)
        if b"Soul vanquished" not in out:
            conn.close()
            return None
        if soul < 19:
            conn.recvuntil(b"> ", timeout=15)

    final = conn.recvall(timeout=15).decode(errors="replace")
    conn.close()
    return final


result = None
for attempt in range(200):
    result = solve_once()
    if result:
        print(f"Won on attempt {attempt + 1}")
        break

if result is None:
    raise SystemExit("exhausted retry budget without winning")

print(result)

flag_env = os.environ.get("flag_flag")
if flag_env and flag_env not in result:
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in output")
