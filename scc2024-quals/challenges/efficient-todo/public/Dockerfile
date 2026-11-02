FROM cybersecnatlab/challenge-jail@sha256:7bf77225063b039960f654307cf5d6f977f892ff548606357a2e8fe8067d0a88
COPY ./todo /home/user/chall
COPY ./libc.so.6 /home/user/
COPY ./ld-linux-x86-64.so.2 /home/user/
COPY ./libs /home/user/libs

ENV SET_INTERPRETER /home/user/libs/ld-linux-x86-64.so.2
ENV SET_RPATH /home/user/libs
EXPOSE 1337
ENV TIMEOUT=120
