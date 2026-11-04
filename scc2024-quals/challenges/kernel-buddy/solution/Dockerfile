FROM python:3.12-slim-bookworm
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev hashcash && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY exploit.c ./
RUN gcc -o exploit -static -pthread exploit.c
COPY solve.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
