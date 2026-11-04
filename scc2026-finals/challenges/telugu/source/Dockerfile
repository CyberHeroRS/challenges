FROM ubuntu:20.04
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y socat

COPY ./main /app/main
COPY ./libc.so.6 /app/libc.so.6
COPY ./ld-linux-x86-64.so.2 /app/ld-linux-x86-64.so.2
COPY ./flag.txt /app/flag.txt

CMD ["socat", "-T", "30", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/app/main"]
