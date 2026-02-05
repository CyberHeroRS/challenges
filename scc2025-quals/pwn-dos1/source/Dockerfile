FROM cybersecnatlab/socaz:debian-bullseye@sha256:1a42f2deb6fd1e9d35a30b3ffd9f51bf02afd157da13e3c87b968009988e135f
RUN apt update && apt install -y dosbox python3 socat
RUN useradd -m user
COPY piton.py /home/user/chall
COPY a /home/user/a
COPY b /home/user/b
COPY dosbox.conf /home/user/
EXPOSE 9198
CMD socaz --bind 9198 --cmd "/home/user/chall"
