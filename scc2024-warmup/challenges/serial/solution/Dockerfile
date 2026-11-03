FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine64 util-linux && \
    rm -rf /var/lib/apt/lists/*
# Debian's wine64 package ships only /usr/lib/wine/wine64 (no /usr/bin/wine* at
# all); the binary also only works when its own name/argv[0] is "wine64" (wine
# refuses to exec as "wine"), so extend PATH instead of symlinking it.
ENV PATH="/usr/lib/wine:${PATH}"
RUN pip install --no-cache-dir pefile==2024.8.26
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# serial.exe (the real, password-protected binary) is bind-mounted in at test time.
# solv.py algebraically reverses the four real arithmetic checks performed by the
# binary (see solve.py docstring) to find every candidate serial satisfying them,
# attempts a genuine dynamic run of each candidate against the real binary under
# Wine (through a pty -- this console app's WriteConsoleW silently no-ops on a
# plain pipe, which is what Docker gives stdout by default), and falls back to
# reproducing the binary's own verified XOR-decrypt logic (reading the real
# ciphertext bytes directly out of the PE image) if Wine is unavailable.
# Passes only when the solver exits cleanly and recovers the real flag.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
