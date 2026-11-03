FROM node:20-slim
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 && \
    rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py run_source.js ./
# source.js (the real, unmodified challenge page logic) is bind-mounted in at
# test time. solve.py recovers the repeating-XOR password via known-plaintext
# analysis, then hands it to run_source.js, which executes the real
# source.js inside a Node vm sandbox exactly as a browser would. Passes only
# when the solver exits cleanly and recovers the real flag.
CMD ["sh", "-c", "python3 solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
