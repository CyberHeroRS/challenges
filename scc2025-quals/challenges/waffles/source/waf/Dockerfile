FROM rust:1.85.1-slim-bookworm as builder

WORKDIR /app

COPY . .

RUN cargo build --release

FROM debian:bookworm-slim

RUN useradd -m user

WORKDIR /app
COPY --from=builder /app/target/release/waf .

RUN chown user:user waf
USER user

EXPOSE 8000

CMD ["./waf"]
