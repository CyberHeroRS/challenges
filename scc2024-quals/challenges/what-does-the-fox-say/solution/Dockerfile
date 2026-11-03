FROM python:3.11-slim-bookworm
# libnss3 provides libnss3.so, which solve.py loads via ctypes to replicate
# Firefox's own PK11SDR_Decrypt call and recover the saved login password.
RUN apt-get update && apt-get install -y --no-install-recommends libnss3 \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# forensics_what_does_the_fox_say.zip is bind-mounted read-only at runtime
# (see challenge.yaml test.mounts) from the challenge's public/ directory.
CMD ["sh", "-c", "python solve.py > /tmp/out 2>/tmp/err; status=$?; cat /tmp/err >&2; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
