# The solver mirrors the service's rand(), so it needs the same glibc (2.39) as the service image.
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-dev gcc && rm -rf /var/lib/apt/lists/* \
 && pip3 install --no-cache-dir --break-system-packages pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY sol.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python3 sol.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
