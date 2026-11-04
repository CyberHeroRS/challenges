# web-room-squatters

**Category:** web  
**Author:** jvvan

## Description

We just launched a new chat app! Unlimited rooms, messages, and unlimited fun! We are 100% privacy-focused, but be careful what you send... there might be some lurkers!

## Writeup

### Vulnerability

Room metadata lives in SQLite and is managed through the REST API, while live subscriptions live only inside Socket.io rooms.

`DELETE /api/rooms/:slug` removes the SQLite row, but it never removes or disconnects sockets that already joined the Socket.io room with that slug. If the same slug is created again later, any stale socket still sitting in that Socket.io room receives new broadcasts automatically.

### Intended solution

The source reveals an internal admin routine in `src/services/adminBot.js`. Every 60 seconds it creates a room whose slug is derived from the current minute:

```js
function generateSlug() {
  return `my-secret-room-${Math.floor(Date.now() / 60000)}`;
}
```

The bot assigns a fresh random password each cycle, authenticates over WebSockets, and sends a message containing the flag. The password is not brute-forceable and changes every run. However, because the slug is predictable from the source, an attacker can squatt the next slug before the bot does.

To exploit the bug:

1. Compute the current slug: `my-secret-room-${Math.floor(Date.now() / 60000)}`.
2. Create that room with any password you know.
3. Join it over WebSockets using your password.
4. Delete it through `DELETE /api/rooms/<slug>`.
5. Stay connected (your socket remains in the Socket.io room despite the REST deletion) and wait for the bot's next cycle.

When the admin bot recreates the same slug and broadcasts the flag, your stale socket receives the message without ever needing the new password.
