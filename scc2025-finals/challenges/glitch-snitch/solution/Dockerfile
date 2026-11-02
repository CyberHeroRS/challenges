FROM rust:1.86-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev ca-certificates && \
    apt-get clean

WORKDIR /solution/check
COPY check/ ./
RUN cargo build --release

# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "./target/release/check > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
