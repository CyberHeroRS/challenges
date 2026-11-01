#FROM ubuntu:24.04
FROM cybersecnatlab/challenge-jail:ubuntu-noble@sha256:2d1e046fa7bb27a6b7d1dba44379b722c0498b40bf9db1a84c47be1ecc09752a

EXPOSE 1337

COPY app /home/user/chall
COPY libc.so.6 /home/user/libc.so.6

ENV TIMEOUT=120