FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome colorama

COPY server.py /srv/server.py
ENV FLAG=SCC{W3_D0_N07_3ND0R53_G4MBL1NG}

EXPOSE 9112

RUN useradd --create-home --uid 1000 user
USER user
CMD socat tcp-l:9112,reuseaddr,fork exec:"python3 /srv/server.py",pty,raw,echo=0,stderr
