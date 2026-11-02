FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY hades_ii.py /srv/hades_ii.py
COPY flag.txt /flag.txt

EXPOSE 13301

RUN useradd --create-home --uid 1000 user
USER user
CMD socat tcp-l:13301,reuseaddr,fork exec:"python3 /srv/hades_ii.py",pty,raw
