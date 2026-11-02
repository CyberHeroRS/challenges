import os
import re

import requests

SITE_URL = os.environ["SERVICE_APP_MAIN_ENDPOINT"]


def main():
    # Part 1: hidden inside an HTML comment on the index page.
    index = requests.get(f"{SITE_URL}/").text
    part1 = re.search(r"Here is the first part: (.*?)-->", index).group(1)

    # Part 2: hidden inside a CSS comment.
    style = requests.get(f"{SITE_URL}/style.css").text
    part2 = re.search(r"Second part: (\S+)", style).group(1)

    # Part 3: hidden inside a JS comment.
    script = requests.get(f"{SITE_URL}/script.js").text
    part3 = re.search(r"in a comment: (\S+)", script).group(1)

    # Part 4 + 5: the API response body carries part 4 and a custom
    # response header carries part 5.
    api = requests.get(f"{SITE_URL}/api/fourth")
    part4 = api.json()["fourth"]
    part5 = api.headers["Last-Flag-Part"]

    flag = part1 + part2 + part3 + part4 + part5
    print(f"Flag: {flag}")


if __name__ == "__main__":
    main()
