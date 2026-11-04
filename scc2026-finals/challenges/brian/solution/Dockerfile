# The challenge image builds `main` against ubuntu:26.04's own libc, but the
# bundled source/libc.so.6 reference file is stale (GLIBC 2.42 vs the actual
# deployed ubuntu:26.04 image's 2.43) -- symbol offsets differ enough that
# GOT-overwrite addresses computed from the bundled file are wrong. Pull the
# real libc straight from the same base image instead of trusting the
# bundled .so.
FROM ubuntu:26.04 AS libs

FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY --from=libs /lib/x86_64-linux-gnu/libc.so.6 ./libc.so.6
COPY exploit.py ./
# main is bind-mounted in at test time (see challenge.yaml's test[0].mounts).
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python exploit.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_flag\" /tmp/out"]
