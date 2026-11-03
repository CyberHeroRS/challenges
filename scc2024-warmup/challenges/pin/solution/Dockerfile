FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine64 && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pefile==2024.8.26
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# pin.exe (the real binary) is bind-mounted in at test time. solve.py derives the 3-digit
# PIN directly from the XOR key embedded in the binary's .data section (pin[i] = key[i] ^
# "SCC"[i], the exact relation the binary itself checks), then attempts a genuine dynamic
# run under Wine -- this PE only imports KERNEL32/USER32/SHELL32 (no debug-CRT DLLs like
# "vault" had), so Wine can actually execute it -- and falls back to reproducing the
# verified out[i] = key[i] ^ pin[i % 3] flag-building logic statically if Wine is
# unavailable. Passes only when the solver exits cleanly and recovers the real flag.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
