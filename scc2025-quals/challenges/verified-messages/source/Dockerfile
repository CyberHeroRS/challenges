FROM ubuntu:22.04

RUN apt update && apt install -y socat python3-pip
RUN pip install PyCryptodome

COPY server.py /srv/server.py
ENV FLAG=SCC{4dmin_4sked_m3_wh4ts_a_P0p_g4dg3t__321_sk1d}

EXPOSE 9113

CMD socat tcp-l:9113,reuseaddr,fork exec:"python3 /srv/server.py",pty,raw,echo=0,stderr