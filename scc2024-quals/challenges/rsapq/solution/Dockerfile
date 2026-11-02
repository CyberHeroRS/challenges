FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends gcc libgmp-dev libmpfr-dev libmpc-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pycryptodome==3.21.0 gmpy2==2.2.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solv.py ./
# output.txt (the intercepted RSA data) is bind-mounted in by the test runner.
# The attack exploits (p+q)^e == p^e + q^e (mod n) together with the leaked
# ctd = d^e mod n to recover p+q via a Franklin-Reiter related-message attack,
# factor n, and decrypt the flag ciphertext. The real flag is 255 chars long,
# which exceeds the challenge.yaml flag body length limit (127), so the test
# verifies the solver's exact output against a pinned SHA-256 hash instead
# (same approach as the forget-me-not reference challenge).
CMD ["sh", "-c", "python solv.py | tee /tmp/out && sha256sum /tmp/out | grep -q '^361d5ed790706f39026513bcb3e427172e7df6fb70bbd1170a384b805a4f3311[[:space:]]'"]
