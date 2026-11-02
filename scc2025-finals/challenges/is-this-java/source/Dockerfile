FROM ubuntu:24.04

EXPOSE 1337

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get -y install socat coreutils

COPY chall/flag.txt /
COPY chall/isthisjava /

RUN chmod 555 /isthisjava && \
    chmod 444 /flag.txt

# Ubuntu 24.04 ships the non-root user ubuntu (UID 1000).
USER ubuntu
CMD socat -T 30 \
    TCP-LISTEN:1337,nodelay,reuseaddr,fork \
    EXEC:"stdbuf -i0 -o0 -e0 /isthisjava"
