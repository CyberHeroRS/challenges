FROM python:3.11-slim

RUN apt-get update && apt-get install -y socat \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pycryptodome

WORKDIR /app

COPY patrick.py .

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 patrick.py',pty,stderr,setsid,sigint,echo=0"]