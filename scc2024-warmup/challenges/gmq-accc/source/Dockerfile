# Build rust binary
FROM rust:latest as builder

WORKDIR /usr/src/challenge

COPY ./challenge/Cargo.toml ./challenge/Cargo.lock ./
COPY ./challenge/src ./src

RUN cargo build --release


FROM cybersecnatlab/challenge-jail:debian-bullseye@sha256:b8d084f32c1917d97d0ce8de6ae74d561c620aa6e87fb7b19f3a3f1b4a03d9c2
COPY --from=builder /usr/src/challenge/target/release/alien_communication /home/user/chall
EXPOSE 1337
ENV TIMEOUT=30
