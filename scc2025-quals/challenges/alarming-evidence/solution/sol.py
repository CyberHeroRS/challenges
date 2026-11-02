import os

from analyze import analyze
from pwn import *

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "access.log")

# This raises (and aborts before ever touching the network) unless the log
# genuinely contains a sustained sqlmap SQLi campaign followed by a directory
# traversal against /blog/admin that leaks a file under secret/. Only once
# that's confirmed do we have the 10 answers the live service expects.
answers_dict = analyze(LOG_PATH)
print("Derived answers from access.log:")
for k, v in answers_dict.items():
    print(f"  {k}: {v}")

answers = [
    answers_dict["domain"],
    answers_dict["ip"],
    answers_dict["isp"],
    answers_dict["browser"],
    answers_dict["os"],
    answers_dict["tool_version"],
    answers_dict["technique"],
    answers_dict["payload"],
    answers_dict["route"],
    answers_dict["sensitive_file"],
]

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

for i, answer in enumerate(answers, start=1):
    p.recvuntil(b"Answer: ")
    p.sendline(answer.encode())

print(p.recvall(timeout=10).decode(errors="replace"))
