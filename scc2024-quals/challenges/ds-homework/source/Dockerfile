FROM ubuntu:22.04 AS app

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app
COPY source.cpp .
COPY flag.txt .
RUN g++ source.cpp -ggdb -Wall -fstack-protector -Wl,-z,relro,-z,now -o run

FROM cybersecnatlab/challenge-jail@sha256:7bf77225063b039960f654307cf5d6f977f892ff548606357a2e8fe8067d0a88
COPY --from=app /app/run /home/user/chall
COPY --from=app /lib/x86_64-linux-gnu /home/user/libs

ENV SET_INTERPRETER /home/user/libs/ld-linux-x86-64.so.2
ENV SET_RPATH /home/user/libs
EXPOSE 1337
ENV TIMEOUT=120
