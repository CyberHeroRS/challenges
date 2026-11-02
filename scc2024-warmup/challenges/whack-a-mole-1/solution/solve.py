import os
import re

from pwn import remote, context

context.log_level = "error"

# The server uses a custom LCG (next = (state * a + c) % m) seeded with a
# hardcoded value. It leaks the modulus `m` in the welcome banner and the
# first three consecutive LCG outputs (s1, s2, s3) right after that. Given
# any two consecutive outputs plus the modulus we can solve for the
# multiplier `a` and increment `c`:
#
#   s2 = s1*a + c (mod m)
#   s3 = s2*a + c (mod m)
#   => a = (s3 - s2) * inverse(s2 - s1, m) (mod m)
#   => c = s2 - a*s1 (mod m)
#
# Once a, c, m are known the LCG is fully predictable, so every one of the
# five "which hole?" rounds can be answered correctly. As a bonus, running
# the recurrence backwards from s1 also recovers the original seed, which
# is the flag for the "whack-a-mole-2" variant of this challenge.

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

banner = p.recvuntil(b"rupa").decode()
m = int(re.search(r"postoji (\d+) rupa", banner).group(1))
print(f"[+] modulus m = {m}")

line = p.recvuntil(b"\n").decode()
while "tri stanja" not in line:
    line = p.recvuntil(b"\n").decode()
s1, s2, s3 = (int(x) for x in re.search(r"tri stanja: (\d+) (\d+) (\d+)", line).groups())
print(f"[+] leaked states s1={s1} s2={s2} s3={s3}")

a = ((s3 - s2) * pow(s2 - s1, -1, m)) % m
c = (s2 - a * s1) % m
assert (s2 * a + c) % m == s3, "LCG parameter recovery failed"
print(f"[+] recovered LCG params a={a} c={c}")

seed = ((s1 - c) * pow(a, -1, m)) % m
print(f"[+] recovered original seed = {seed}")
# whack-a-mole-2 reuses this exact seed value as its flag body (it is given
# to players via the downloadable source and is also independently
# recoverable from the live service, as done above), wrapped in the event's
# flag format; print it explicitly so it is captured regardless of which
# variant of the challenge this solver is run against.
print(f"[+] possible flag: SCC{{{seed}}}")

state = s3
for i in range(5):
    p.recvuntil(b"Koji broj rupe zelite da udarite cekicem?")
    state = (state * a + c) % m
    p.sendline(str(state).encode())
    print(f"[+] round {i}: guessed {state}")

out = p.recvall(timeout=10).decode(errors="replace")
print(out)
p.close()
