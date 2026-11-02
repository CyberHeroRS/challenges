# Build context: the challenge directory.
FROM debian:bookworm-slim AS compiler
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build

# Deployed binary, built from the source containing the real flag.
FROM compiler AS service-binary
COPY source/source.c .
RUN gcc source.c -o bananas

# Participant binary, built from the published source with a placeholder flag.
FROM compiler AS participant-binary
COPY public/source.c .
RUN gcc source.c -o bananas

FROM scratch AS participant
COPY --from=participant-binary /build/bananas /bananas

FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user

WORKDIR /home/user
COPY --from=service-binary --chmod=0555 /build/bananas ./chall
EXPOSE 1337
ENV TIMEOUT=120
USER user

CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
