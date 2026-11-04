FROM debian:trixie-slim

RUN apt-get update && apt-get install -y socat python3 && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf

WORKDIR /home/ctf
RUN mkdir /home/ctf/glibc
COPy ./glibc ./glibc
COPY ./bigvm2 .
COPY ./runner.py .
RUN chmod +x bigvm2
RUN chmod +x runner.py

EXPOSE 1337

CMD bash -c "echo \$FLAG > /home/ctf/flag.txt && unset FLAG && exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/home/ctf/runner.py,su=ctf"