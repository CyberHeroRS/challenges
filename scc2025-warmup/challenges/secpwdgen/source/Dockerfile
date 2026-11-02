FROM rust:1.95-bookworm AS builder
WORKDIR /app
COPY src ./src
COPY Cargo.toml ./
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
WORKDIR /home/user
COPY --from=builder --chmod=0555 /app/target/release/secpwdgen ./chall
EXPOSE 1337
ENV TIMEOUT=120
USER user
CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
