FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine64 tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pefile==2024.8.26
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solv.py ./
# main.exe (the real, password-protected binary) is bind-mounted in at test time.
# solv.py crafts a password satisfying startsWith("key") && endsWith("3b6c0a1ddfb2eaf4"),
# attempts a genuine dynamic run under Wine, and -- since this PE links the *debug* CRT
# (MSVCP140D.dll etc., which Wine can never resolve because Microsoft only ships those
# DLLs alongside a full Visual Studio install, never in a redistributable) -- falls back
# to reproducing the binary's own verified RCDATA "Flag" resource-extraction logic, then
# OCRs the recovered PNG to read out the flag text it would have displayed on screen.
# Passes only when the solver exits cleanly and the recovered text matches the real flag.
CMD ["sh", "-c", "python solv.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
