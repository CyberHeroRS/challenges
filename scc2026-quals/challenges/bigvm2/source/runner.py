#!/usr/bin/python3

import subprocess
import tempfile
import sys
import os

def run_payload(hex_input):
    try:
        raw_bytes = bytes.fromhex(hex_input.replace(" ", "").replace("\n", ""))
    except ValueError:
        print("Invalid hex input.")
        return

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    try:
        print(f"[*] Executing with payload: {tmp_path}")
        subprocess.run(["./bigvm2", tmp_path])
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_payload(sys.argv[1])
    else:
        user_input = input("Enter hex bytes: ")
        run_payload(user_input)