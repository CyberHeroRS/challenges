FROM python:3.12-slim

EXPOSE 1337

RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir pycryptodome

COPY rtfm-cdef0123.py /

RUN chmod 555 /rtfm-cdef0123.py

CMD socat -T 100 \
    TCP-LISTEN:1337,nodelay,reuseaddr,fork \
    EXEC:"stdbuf -i0 -o0 -e0 python /rtfm-cdef0123.py"
    