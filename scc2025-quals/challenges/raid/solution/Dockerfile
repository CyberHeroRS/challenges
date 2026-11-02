FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /solution
COPY sol.c ./
RUN gcc sol.c -o sol
# The solver rebuilds the lost disks in place, so it runs on a writable copy of the published ones.
CMD ["sh", "-c", "mkdir -p /tmp/run && cp -r /inputs/disks /tmp/run/ && cd /tmp/run && /solution/sol > /tmp/out; status=$?; cat /tmp/out output.txt > /tmp/all 2>/dev/null; cat /tmp/all; [ \"$status\" -eq 0 ] && grep -qaF \"$flag_main\" /tmp/all"]
