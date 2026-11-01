FROM rust:latest AS builder

WORKDIR /app
COPY src ./src
COPY Cargo.toml ./

RUN cargo build --release

FROM cybersecnatlab/challenge-jail:debian-bullseye@sha256:b8d084f32c1917d97d0ce8de6ae74d561c620aa6e87fb7b19f3a3f1b4a03d9c2

WORKDIR /home/user
COPY --from=builder /app/target/release/secpwdgen /home/user/chall

ENV FLAG_IN_ENV=true \
    TIMEOUT=120

EXPOSE 1337