FROM python:3.11-slim

RUN apt-get update && apt-get install -y socat \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pycryptodome

WORKDIR /app

COPY hades_iii.py .

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 hades_iii.py',pty,stderr,setsid,sigint,echo=0"]