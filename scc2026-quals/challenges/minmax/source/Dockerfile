FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf

WORKDIR /home/ctf
COPY ./minmax .
RUN chmod +x minmax

EXPOSE 1337

CMD bash -c "echo \$FLAG > /home/ctf/flag.txt && unset FLAG && exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/ctf/minmax,su=ctf"