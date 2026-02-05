FROM rust:alpine3.18

WORKDIR /build

RUN apk update && apk upgrade && apk add pkgconfig libressl-dev musl-dev --no-cache

COPY rust-toolchain.toml .

# RUN rustup update && \
#     rustup target add wasm32-unknown-unknown && \
#     cargo install trunk
 
RUN rustup target add wasm32-unknown-unknown && cargo install trunk

#RUN trunk build --release

COPY . .

EXPOSE 8080

CMD ["trunk", "serve", "--address", "0.0.0.0"] 