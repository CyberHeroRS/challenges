FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY source.py /srv/chall.py

EXPOSE 13300

CMD socat tcp-l:13300,reuseaddr,fork exec:"python3 /srv/chall.py",pty,raw
