FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /solution
COPY sol.c ./
RUN gcc sol.c -o sol
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "./sol > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
