#!/usr/bin/env python3

import subprocess
import os
import shutil
import tempfile
import sys

temp_dir = tempfile.mkdtemp()
os.chdir(temp_dir)
home_user_dir = '/home/user'

try:
    shutil.copytree(os.path.join(home_user_dir, 'a'), os.path.join(temp_dir, 'a'))
    shutil.copytree(os.path.join(home_user_dir, 'b'), os.path.join(temp_dir, 'b'))
    shutil.copy(os.path.join(home_user_dir, 'dosbox.conf'), temp_dir)
except:
    print("error: contact challenge admin")

flag = os.getenv('FLAG')
if not flag:
    flag = b"SCC{fake_flag}"
with open(os.path.join(temp_dir, 'b/flag.txt'), 'w') as f:
    f.write(flag)

print("Payload length:", flush=True)
size = int(input())
if not 0 < size < 512:
    print("The payload length must be between 0 and 512 bytes")
    exit(0)

print("Payload:", flush=True)
buffer = sys.stdin.buffer.read(size)

with open('b/INPUT.TXT', 'wb+') as f:
    f.write(buffer)
    f.close()

print("starting...", flush=True)

env = os.environ.copy()
env["SDL_VIDEODRIVER"] = "dummy"

devnull = open(os.devnull, 'w')
subprocess.run(['dosbox', '-noconsole', '-conf', 'dosbox.conf'], env=env, stdout=devnull, stderr=devnull)

if os.path.exists('b/OUTPUT.TXT'):
    with open('b/OUTPUT.TXT', 'rb') as f:
        output = f.read()
        print(output, flush=True)
else:
    print("error: b/OUTPUT.TXT missing", flush=True)

shutil.rmtree(temp_dir)
print("ending...", flush=True)
