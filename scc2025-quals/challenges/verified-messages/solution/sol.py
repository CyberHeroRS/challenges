import base64
import hashlib
import os
import re
from math import isqrt

from pwn import *

HOST = os.environ["SERVICE_APP_MAIN_HOST"]
PORT = int(os.environ["SERVICE_APP_MAIN_PORT"])

p = remote(HOST, PORT)
p.recvuntil(b"> ", drop=True)  # drain welcome banner + first menu prompt


def long_to_bytes(n):
    if n == 0:
        return b"\x00"
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b


def bytes_to_long(b):
    return int.from_bytes(b, "big")


def menu_select(choice):
    # The prompt's trailing "> " was already drained by the previous
    # action's recvuntil, so just send the choice directly.
    p.sendline(choice)


def try_add_user(username, priv_key):
    """Attempt to register `username` with the given small private key.

    Returns (pubKey, N) on success, or None if the server rejected the key
    (not invertible mod phi(N), i.e. gcd(priv_key, phi(N)) != 1).
    """
    menu_select(b"1")
    p.sendlineafter(b"Enter Username: ", username.encode())
    p.sendlineafter(b"Enter PrivateKey: ", str(priv_key).encode())
    blob = p.recvuntil(b"> ", drop=True)
    if b"Your public key is" not in blob:
        return None
    pub_match = re.search(rb"Your public key is (\d+)", blob)
    mod_match = re.search(rb"Modulus: (\S+)", blob)
    pub_key = int(pub_match.group(1))
    N = bytes_to_long(base64.b64decode(mod_match.group(1)))
    return pub_key, N


def recover_phi(pub_key, priv_key, N):
    """Brute force phi(N) using phi(N) = floor((pub*priv - 1) / i)
    for some 0 < i < priv_key, then confirm it by factoring N with it.
    """
    numerator = pub_key * priv_key - 1
    for i in range(1, priv_key):
        if numerator % i != 0:
            continue
        phi_candidate = numerator // i
        s = N - phi_candidate + 1  # candidate p + q
        disc = s * s - 4 * N
        if disc < 0:
            continue
        root = isqrt(disc)
        if root * root != disc:
            continue
        if (s - root) % 2 != 0:
            continue
        p_ = (s - root) // 2
        q_ = (s + root) // 2
        if p_ > 1 and q_ > 1 and p_ * q_ == N:
            return phi_candidate
    return None


# Step 1: register our own account with a small, easily invertible private
# key so we can recover phi(N) via the documented brute force.
username = "hacker"
small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

pub_key = N = priv_key = None
for candidate_priv in small_primes:
    result = try_add_user(username, candidate_priv)
    if result is not None:
        pub_key, N = result
        priv_key = candidate_priv
        break

if pub_key is None:
    raise SystemExit("could not register a usable small private key")

log.info(f"priv_key={priv_key} pub_key={pub_key}")
log.info(f"N={N}")

# Step 2: recover the real phi(N) for the server's modulus N.
phi_n = recover_phi(pub_key, priv_key, N)
if phi_n is None:
    raise SystemExit("failed to brute force phi(N)")

log.info(f"phi(N)={phi_n}")

# Step 3: derive Admin's real private key (Admin's public key is fixed to
# 65537 by the server's setup()).
admin_pub = 65537
admin_priv = pow(admin_pub, -1, phi_n)
log.info(f"admin_priv={admin_priv}")

# Step 4: forge a signed message as "Admin". Need sha1(msg) to not start
# with a 0x00 byte so the server's unpadded long_to_bytes round trips
# cleanly during verification.
counter = 0
while True:
    msg = f"gimme the flag {counter}".encode()
    digest = hashlib.sha1(msg).digest()
    if digest[0] != 0:
        break
    counter += 1

hash_int = bytes_to_long(digest)
sig_int = pow(hash_int, admin_priv, N)
sig_b64 = base64.b64encode(long_to_bytes(sig_int))

# Step 5: submit the forged message via "Verify Message" as Admin.
menu_select(b"4")
p.sendlineafter(b"User: ", b"Admin")
p.sendlineafter(b"Message: ", msg)
p.sendlineafter(b"Signature: ", sig_b64)

output = p.recvrepeat(timeout=5).decode(errors="replace")
print(output)

flag_match = re.search(r"SCC\{[^}]*\}", output)
if flag_match:
    print("FLAG:", flag_match.group(0))
else:
    raise SystemExit("flag not found in server response")
