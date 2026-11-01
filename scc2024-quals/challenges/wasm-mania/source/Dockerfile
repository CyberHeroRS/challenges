# Builder
FROM rust:1.76 as builder
WORKDIR /app
RUN rustup toolchain install nightly && rustup default nightly
RUN rustup target add wasm32-unknown-unknown
RUN cargo install trunk miniserve

COPY . .
RUN trunk build --release

# Runtime
FROM gcr.io/distroless/cc-debian12
WORKDIR /app

COPY --from=builder /usr/local/cargo/bin/miniserve /miniserve
COPY --from=builder /app/dist /dist

EXPOSE 8080
ENTRYPOINT ["/miniserve", "/dist", "--spa", "--index", "index.html", "--port", "8080"]
