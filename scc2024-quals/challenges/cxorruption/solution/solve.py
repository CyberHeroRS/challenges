import os

# cxorruption's binary corrupts a file in two reversible passes (per the
# published decompile of its main()):
#   1. for i in range(size-1): buff[i] += buff[i+1]     (forward prefix-sum-ish add)
#   2. buff[i] ^= SECRET_KEY[i % len(SECRET_KEY)]         (repeating-key XOR)
# To recover the original flag file from the real enc.txt, undo step 2 first
# (XOR is self-inverse), then undo step 1 by walking backwards and
# subtracting (the exact inverse of the forward addition chain).

ENC_PATH = "/solution/enc.txt"
SECRET_KEY = b"SECRET_KEY"

with open(ENC_PATH, "rb") as f:
    enc = f.read()

dec = [enc[i] ^ SECRET_KEY[i % len(SECRET_KEY)] for i in range(len(enc))]

for i in range(len(dec) - 1, 0, -1):
    dec[i - 1] = (dec[i - 1] - dec[i]) & 0xFF

flag = "".join(chr(b) for b in dec)
print(flag)

expected = os.environ.get("flag_main")
if expected and expected not in flag:
    print(f"MISMATCH: expected substring {expected!r} not in decoded flag {flag!r}")
    raise SystemExit(1)
