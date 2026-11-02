FROM python:3.12-slim

EXPOSE 1337


RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/*

COPY ./xor_me_many_times.py /

RUN chmod 555 /xor_me_many_times.py

RUN useradd --create-home --uid 1000 user
USER user
ENTRYPOINT []
CMD socat -T 100 \
    TCP-LISTEN:1337,nodelay,reuseaddr,fork \
    EXEC:"stdbuf -i0 -o0 -e0 python /xor_me_many_times.py"
    