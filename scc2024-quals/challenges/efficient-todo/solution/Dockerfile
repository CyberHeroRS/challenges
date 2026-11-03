FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.14.1 z3-solver==4.13.0.0
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# source/libc.so.6 is bind-mounted in at test time (see challenge.yaml's
# test[0].mounts) and is needed to resolve the `initial`/`system`/"/bin/sh"
# offsets relative to the leaked libc_base at solve time.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
