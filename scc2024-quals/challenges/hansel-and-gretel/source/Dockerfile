FROM ubuntu:22.04 AS patch
RUN apt-get update && \
    apt-get install -y --no-install-recommends patchelf && \
    rm -rf /var/lib/apt/lists/*
COPY ./hgp /chall
# Equivalent of the former challenge-jail SET_INTERPRETER/SET_RPATH settings.
RUN patchelf --set-interpreter /home/user/libs/ld-linux-x86-64.so.2 --set-rpath /home/user/libs /chall

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
WORKDIR /home/user
COPY --from=patch --chmod=0555 /chall ./chall
COPY ./libc.so.6 ./
COPY ./ld-linux-x86-64.so.2 ./
COPY ./libs ./libs

EXPOSE 1337
ENV TIMEOUT=120
USER user
CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} ./chall,stderr\""]
