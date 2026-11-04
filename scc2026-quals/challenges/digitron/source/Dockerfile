FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    socat \
    ncurses-bin \
    libncurses5-dev \
    libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

ENV TERM=xterm
ENV TERMINFO=/usr/share/terminfo

WORKDIR /app

COPY digitron.py .
RUN chmod +x digitron.py

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 digitron.py',pty,stderr,setsid,sigint,echo=0"]