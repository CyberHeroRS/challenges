FROM debian:trixie-slim

RUN apt-get update && apt-get install -y socat python3 && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf

WORKDIR /home/ctf
COPY ./watermelon-shop .
RUN chmod +x watermelon-shop

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/home/ctf/watermelon-shop,su=ctf"]