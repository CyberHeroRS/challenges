FROM debian:bullseye-slim AS base
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list

# Same toolchain and flags as the original compile.sh (Debian 11 GCC 10.2.1).
FROM base AS compile
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY source.c .
RUN gcc source.c -o beusX -fstack-protector -Wl,-z,relro,-z,now

# Load the provided glibc; patchelf 0.18 reproduces the published binary's symbol table.
FROM python:3.12-slim-bookworm AS binary
RUN pip install --no-cache-dir patchelf==0.18.0
COPY --from=compile /build/beusX /build/beusX
RUN patchelf --set-interpreter glibc/ld-2.31.so --set-rpath glibc /build/beusX

FROM scratch AS participant
COPY --from=binary /build/beusX /beusX

FROM base
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user

WORKDIR /home/user
COPY --from=binary --chmod=0555 /build/beusX ./chall
COPY ./glibc ./glibc
EXPOSE 1337
ENV TIMEOUT=120
USER user

CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} stdbuf -i0 -o0 -e0 ./chall,stderr\""]
