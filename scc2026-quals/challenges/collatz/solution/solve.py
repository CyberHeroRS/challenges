import os

from pwn import context, remote

context.log_level = "info"

HOST = os.environ.get("SERVICE_COLLATZ_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_COLLATZ_SHELL_PORT", "1337"))

# The server asks for a single starting integer and iterates the Collatz
# step function, declaring a "win" only if the SAME value is ever
# revisited before reaching 1 (and exits silently the moment n==1, so
# the trivial 4->2->1 trajectory never counts).
#
# The Collatz conjecture itself is only about positive integers -- the
# server places no restriction on the sign of the input, and negative
# integers have well-known short non-trivial cycles. Starting at n=-1:
#   -1 is odd (Python's % always matches the divisor's sign, so
#   -1 % 2 == 1), so step(-1) = 3*(-1)+1 = -2.
#   -2 is even, so step(-2) = -2 // 2 = -1.
# That revisits -1 on the very next iteration -- an immediate 2-cycle
# that never touches 1, satisfying the server's win condition at once.

p = remote(HOST, PORT)
p.sendline(b"-1")
output = p.recvall(timeout=10).decode(errors="replace")
p.close()

print(output)

flag_env = os.environ.get("flag_flag")
if flag_env and flag_env not in output:
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {output!r}")
