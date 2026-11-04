FROM debian:trixie-slim

RUN apt-get update && apt-get install -y socat python3 qemu-user && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf

WORKDIR /home/ctf
COPY ./secure-cipher .
COPY ./run.sh .
RUN chmod +x secure-cipher run.sh

EXPOSE 1337

CMD bash -c "echo \$FLAG > /home/ctf/flag.txt && unset FLAG && exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/ctf/run.sh,su=ctf"
