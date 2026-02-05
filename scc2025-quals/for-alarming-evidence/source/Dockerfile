FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY . .

EXPOSE 1501

CMD socat tcp-l:1501,reuseaddr,fork exec:"python3 /usr/src/app/server.py",pty,raw,echo=0,stderr