FROM debian:bullseye-slim@sha256:95a3884fee36b8f33bf32a6bbffa8dffe6cab6089b841cec45fb47c581a2709d

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf

WORKDIR /home/ctf
COPY ./beus3 .
COPY ./libc.so.6 .
COPY ./ld-linux-x86-64.so.2 .
RUN chmod +x beus3

EXPOSE 1337

CMD bash -c "echo \$FLAG > /home/ctf/flag.txt && unset FLAG && exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/ctf/beus3,su=ctf"