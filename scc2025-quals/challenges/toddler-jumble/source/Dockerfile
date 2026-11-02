FROM debian:bullseye-slim AS base
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list

# Same toolchain as the original compile.sh (Debian 11 GCC 10.2.1), then the binary is
# pointed at the provided loader and libc with Debian 11's patchelf.
FROM base AS binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev patchelf && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY chal.c .
RUN gcc chal.c -o chal && \
    patchelf --set-interpreter ld-linux-x86-64.so.2 --set-rpath . chal

FROM scratch AS participant
COPY --from=binary /build/chal /chal

FROM base
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user

WORKDIR /home/user
COPY --from=binary --chmod=0555 /build/chal ./chall
COPY ./libc.so.6 ./ld-linux-x86-64.so.2 ./
EXPOSE 1337
ENV TIMEOUT=120
USER user

CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
