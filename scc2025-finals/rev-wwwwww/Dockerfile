FROM rust:1.86-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y python3 python3-pip python-is-python3 && \
    apt-get clean

WORKDIR /build
COPY . .
RUN pip install -r requirements-build.txt --break-system-packages
RUN cargo build --release

FROM debian:12.10-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y socat coreutils && \
    apt-get clean
WORKDIR /app
COPY --from=builder /build/target/release/wwwwww .
COPY  ./flag.txt .

EXPOSE 1337

ENTRYPOINT [ "socat", "TCP-L:1337,fork,reuseaddr", "exec:stdbuf -i0 -o0 /app/wwwwww" ]
