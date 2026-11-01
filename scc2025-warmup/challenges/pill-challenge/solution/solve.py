#!/usr/bin/env python3
import http.client

chall_host = "pill.playground.cyberhero.rs"
chall_port = 443


def start():
    conn = http.client.HTTPSConnection(chall_host, chall_port)
    conn.request("POST", "/start")
    res = conn.getresponse()
    return res.getheader("x-session-id")


def round(session_id):
    redConn = http.client.HTTPSConnection(chall_host, chall_port)
    redConn.connect()
    redConn.putrequest("POST", "/guess")
    redConn.putheader("x-session-id", session_id)
    redConn.putheader("Content-Type", "text/plain")
    redConn.putheader("Content-Length", len("red"))
    redConn.endheaders()

    blueConn = http.client.HTTPSConnection(chall_host, chall_port)
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
    conn = http.client.HTTPSConnection(chall_host, chall_port)
    conn.request("GET", "/status", headers={"x-session-id": session_id})
    res = conn.getresponse()
    return res.read().decode()


session_id = start()
for i in range(1, 101):
    current = round(session_id)
    print("Round", i, ":", current, "->", status(session_id))
