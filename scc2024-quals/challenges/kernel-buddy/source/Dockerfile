FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y qemu qemu-system-x86 qemu-utils socat cpio gzip wget hashcash curl

EXPOSE 1337

RUN useradd -d /home/ctf -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd
RUN ulimit -c 0

WORKDIR /home/ctf
COPY bzImage ./bzImage
COPY run.sh ./run.sh
COPY initramfs.cpio.gz ./initramfs.cpio.gz
RUN chmod +x *.sh
RUN chmod 666 ./initramfs.cpio.gz

EXPOSE 1337
USER ctf
CMD socat tcp-l:1337,reuseaddr,fork EXEC:"./run.sh",pty,stderr
