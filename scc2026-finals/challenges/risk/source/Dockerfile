FROM ubuntu:26.04
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y socat qemu-user

COPY ./main /app/main
COPY ./flag.txt /app/flag.txt

CMD ["socat", "-T", "30", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:qemu-riscv32 /app/main"]
