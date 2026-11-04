FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    socat && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY collatz.py .

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 collatz.py',pty,stderr,setsid,sigint,echo=0"]