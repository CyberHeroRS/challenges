import ast

# The modulus is leaked directly in public/source.py (hardcoded in LCG.__init__),
# but the multiplier, increment and initial state are all random/secret.
mod = 8471050156910645297199092184997948739352218102032175415195952882946019032523893352683847323674258073

with open("./out.txt", "r") as f:
    lines = [line for line in f.read().splitlines() if line.strip()]

outs = ast.literal_eval(lines[0])   # 20 consecutive LCG outputs: s1 .. s20
enc = ast.literal_eval(lines[1])    # encrypt(FLAG) ciphertext bytes

# Classic known-modulus LCG attack: from three consecutive outputs
#   s2 = mul*s1 + inc (mod m)
#   s3 = mul*s2 + inc (mod m)
# subtracting gives s3 - s2 = mul * (s2 - s1) (mod m), so mul is recoverable
# via modular inverse (gcd of the delta with m is 1 almost always since m is
# effectively prime here).
s1, s2, s3 = outs[0], outs[1], outs[2]
mul = (s3 - s2) * pow(s2 - s1, -1, mod) % mod
inc = (s3 - mul * s2) % mod

# Sanity-check the recovered parameters against the full observed sequence.
for i in range(len(outs) - 1):
    assert (mul * outs[i] + inc) % mod == outs[i + 1], "recovered LCG params are wrong"

# encrypt() advances the generator one more step before XOR-ing with the
# flag, so the keystream state is s21 (one step past the last leaked output).
s20 = outs[-1]
s21 = (mul * s20 + inc) % mod

L = len(enc)
bstate = s21.to_bytes(L * 2, byteorder="big")
flag = bytes(c ^ k for c, k in zip(enc, bstate[:L]))

print(flag.decode())
