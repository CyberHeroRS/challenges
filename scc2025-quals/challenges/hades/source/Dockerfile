FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY hades.py /srv/hades.py
COPY flag.txt /flag.txt

EXPOSE 13300

RUN useradd --create-home --uid 1000 user
USER user
CMD socat tcp-l:13300,reuseaddr,fork exec:"python3 /srv/hades.py",pty,raw
