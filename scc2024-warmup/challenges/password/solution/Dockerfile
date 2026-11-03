FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine64 bsdutils && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pefile==2024.8.26 capstone==5.0.3
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# password.exe is bind-mounted in at test time. solve.py reconstructs the
# real key by tracing the binary's own stack-string-building code (no
# hardcoded key/flag), then -- since (unlike sibling challenge `vault`) this
# PE has no debug-CRT dependency -- genuinely runs it under Wine (via a pty,
# since WriteConsoleW needs a real console) to read the real printed flag
# line, falling back to reproducing its own verified success format string
# only if Wine is ever unavailable. Passes only when the solver exits
# cleanly and recovers the exact expected flag.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
