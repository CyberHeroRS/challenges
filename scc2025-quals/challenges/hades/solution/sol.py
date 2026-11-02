import os
import re
import random

from pwn import remote

# The oracle game: each "soul" pair consists of one NextGenPRF(0) (true random,
# a fresh urandom(32) XORed with the message on every call) and one
# NextGenPRF(1) (pseudorandom, AES-ECB under a fixed per-round key). For a
# FIXED 16-byte message, the pseudorandom side always returns the identical
# ciphertext while the true-random side returns a different value every time
# it's queried. So we ask the same question twice via option "3" and see
# which side (left/right) repeated its answer -- that side is the
# pseudorandom one, so the OTHER side is the true random soul to pick.
#
# Budget note: the service grants only 100 total judgement queries but there
# are 52 souls, and a fully certain verdict costs 2 queries (one question
# asked twice). 52 * 2 = 104 > 100, so we can only afford full verification
# for 50 souls; the service doesn't let us even try to ask once budget hits
# zero (it fails the round outright), so for the remaining souls we spend no
# queries and guess blindly (50% each). That gives a 25% chance of clearing
# every soul in a single connection; on failure we just reconnect and retry
# until we get lucky on those two blind rounds.

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

SOULS = 52
QUESTIONS_BUDGET = 100
MSG = b"41" * 16  # 32 hex chars -> 16 raw bytes, fixed across both queries
MAX_ATTEMPTS = 300


def ask(io):
    io.sendlineafter(b"> ", b"3")
    io.recvuntil(b"State your question for the souls: ")
    io.sendline(MSG)
    io.recvuntil(b"The left soul screams: ")
    left = io.recvline().strip()
    io.recvuntil(b"The right soul screams: ")
    right = io.recvline().strip()
    return left, right


def attempt():
    io = remote(HOST, PORT, timeout=10)
    budget = QUESTIONS_BUDGET

    for _ in range(SOULS):
        if budget >= 2:
            left1, _ = ask(io)
            left2, _ = ask(io)
            budget -= 2
            # left repeated its answer -> left is the deterministic PRF ->
            # right is the true random soul.
            door = b"2" if left1 == left2 else b"1"
        else:
            # Out of judgement budget: no query can add information, so
            # guess blindly rather than wasting a round on a query the
            # service won't even allow (it fails immediately at 0 budget).
            door = random.choice([b"1", b"2"])
        io.sendlineafter(b"> ", door)

    data = io.recvall(timeout=10).decode(errors="replace")
    io.close()

    match = re.search(r"SCC\{[^}]*\}", data)
    return match.group(0) if match else None


def main():
    for attempt_no in range(1, MAX_ATTEMPTS + 1):
        try:
            flag = attempt()
        except Exception as exc:  # EOF/timeout on a wrong blind guess, etc.
            print(f"attempt {attempt_no} failed: {exc}")
            flag = None

        if flag:
            print("FLAG:", flag)
            print("attempts:", attempt_no)
            return

    raise SystemExit(f"failed to recover the flag after {MAX_ATTEMPTS} attempts")


if __name__ == "__main__":
    main()
