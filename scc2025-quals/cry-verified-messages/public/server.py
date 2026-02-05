from Crypto.Util import number
import Crypto.Hash.SHA1 as sha1
import base64
import os

WELCOME="""
Welcome to our public bulletin board.
Create signed messages and verify their authenticity

!! Online features are not yet implemented !!
"""

MENU="""
Choose an action:
    1.) Create User
    2.) Create Message
    3.) View Users
    4.) Verify Message
"""

p = number.getPrime(512)
q = number.getPrime(512)

N = p*q
L = (p-1)*(q-1)

Users = {}

def enc(b, user):
    return number.long_to_bytes(pow(number.bytes_to_long(b), Users[user]['privateKey'], N))

def dec(b, user):
    return number.long_to_bytes(pow(number.bytes_to_long(b), Users[user]['pubKey'], N))

def generateMessage(msg, user):
    hash = sha1.new(msg.encode()).digest()
    sig = enc(hash, user)
    sig = base64.b64encode(sig)
    return msg,sig
    
def verify(user, msg, sig):
    if(not user in Users.keys()):
        return
    hash = sha1.new(msg).digest()
    a = dec(base64.b64decode(sig), user)
    return a == hash

def keypair(key1):
    key2 = pow(key1,-1,L)
    return key2

def addUser():
    global Users
    username = input("Enter Username: ")
    if(username in Users.keys()):
        print("User already exists")
        return
    try:
        privateKey = int(input("Enter PrivateKey: "))
        pubKey = keypair(privateKey)
    except (ValueError, TypeError):
        print("Can't generate keypair for given key")
        return

    if(privateKey in map(lambda x: x['pubKey'],Users.values())):
        print("Keypair already exists")
        return
    if(pubKey in map(lambda x: x['pubKey'],Users.values())):
        print("Keypair already exists")
        return
    print(f"Your public key is {pubKey}")
    print(f"Modulus: {base64.b64encode((number.long_to_bytes(N))).decode()}")
    Users[username] = {"pubKey": pubKey, "privateKey": privateKey}

def postMessage():
    username = input("Username: ")
    if(username == "Admin"):
        print("Not permitted")
        return
    if(not username in Users.keys()):
        print("User doesn't exist") 
        return
    msg, sig = generateMessage(input("Message: "), username)
    print(f"{username}: {msg} (sig: {sig})")
    
def verifyMessage():
    username = input("User: ")
    message = input("Message: ").encode()
    signature = input("Signature: ").encode()
    if not verify(username, message, signature):
        print("Failed to verify message")
        return
    
    print("Message is verified")

    if username == "Admin":
        print(f"Oh I see, you've talked to an admin: {os.getenv('FLAG','SCC{REDACTED}')}")

def setup():
    AdminPubKey = 65537
    AdminPrivateKey = keypair(AdminPubKey)
    Users['Admin'] = {'pubKey': AdminPubKey, 'privateKey': AdminPrivateKey}


if __name__ == '__main__':
    setup()
    print(WELCOME)
    while 1:
        print(MENU)
        opt = input("> ")
        match opt:
            case '1':
                addUser()
            case '2':
                postMessage()
            case '3':
                for key, val in Users.items():
                    print(f"User: {key}\n Public Key: {val['pubKey']}\n")
            case '4':
                verifyMessage()
            case default:
                print("Invalid option")
        
