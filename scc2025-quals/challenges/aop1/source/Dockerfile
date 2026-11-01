FROM cybersecnatlab/challenge-jail:debian-bullseye@sha256:b8d084f32c1917d97d0ce8de6ae74d561c620aa6e87fb7b19f3a3f1b4a03d9c2

COPY ./aop1 /home/user/chall
COPY ./glibc /home/user/glibc

EXPOSE 1337

ENV FLAG_IN_ENV=true
ENV TIMEOUT=300