FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY cards.py /srv/cards.py
RUN useradd --create-home --uid 1000 user
USER user

EXPOSE 13300

CMD socat tcp-l:13300,reuseaddr,fork exec:"python3 /srv/cards.py",pty,raw
