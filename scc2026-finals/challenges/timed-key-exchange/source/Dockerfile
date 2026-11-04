FROM python:3.12-slim

EXPOSE 1337

RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/*

COPY tke.py /

RUN chmod 555 /tke.py

ENTRYPOINT []
CMD socat -T 600 \
    TCP-LISTEN:1337,nodelay,reuseaddr,fork \
    EXEC:"stdbuf -i0 -o0 -e0 python /tke.py"
    