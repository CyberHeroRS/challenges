#FROM ubuntu:18.04
FROM cybersecnatlab/challenge-jail:debian-bullseye@sha256:b8d084f32c1917d97d0ce8de6ae74d561c620aa6e87fb7b19f3a3f1b4a03d9c2

EXPOSE 1337


COPY libc.so.6 /home/user/libc.so.6
COPY ld-linux-x86-64.so.2 /home/user/ld-linux-x86-64.so.2
COPY app /home/user/chall

ENV TIMEOUT=120
