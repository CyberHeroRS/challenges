FROM debian:trixie-slim@sha256:b29a157cc8540addda9836c23750e389693bf3b6d9a932a55504899e5601a66b

RUN apt-get update && \
    apt-get install -y socat gcc libc6-dev libbpf1 vim && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 ctf

WORKDIR /home/ctf

COPY ./binary/callgate ./callgate
COPY ./binary/callgate.bpf.o ./callgate.bpf.o

RUN chmod +x callgate

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 1337

CMD ["/start.sh"]