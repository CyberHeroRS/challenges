# Build context: the challenge directory.
FROM debian:bookworm-slim AS binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY source/source.c .
RUN gcc source.c -o login_form

FROM scratch AS participant
COPY --from=binary /build/login_form /login_form

FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user

WORKDIR /home/user
COPY --from=binary --chmod=0555 /build/login_form ./chall
COPY source/flag.txt ./
EXPOSE 1337
ENV TIMEOUT=120
USER user

CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
