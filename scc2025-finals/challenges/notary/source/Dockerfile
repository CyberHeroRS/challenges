FROM ubuntu:18.04 AS base

# Same toolchain and flags as build.sh (Ubuntu 18.04 GCC 7.5); byte-identical to the
# published binary. It loads the provided glibc 2.27 from its working directory.
FROM base AS binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY app.c .
RUN gcc -o app app.c -Wl,--rpath=. -Wl,--dynamic-linker=./ld-linux-x86-64.so.2

FROM scratch AS participant
COPY --from=binary /build/app /app

FROM base
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user

WORKDIR /home/user
COPY --from=binary --chmod=0555 /build/app ./chall
COPY libc.so.6 ld-linux-x86-64.so.2 ./
EXPOSE 1337
ENV TIMEOUT=120
USER user

CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
