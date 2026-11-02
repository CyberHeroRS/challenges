FROM ubuntu:22.04 AS app

RUN apt-get update && apt-get install -y build-essential patchelf

WORKDIR /app
COPY source.cpp .
COPY flag.txt .
RUN g++ source.cpp -ggdb -Wall -fstack-protector -Wl,-z,relro,-z,now -o run
# Equivalent of the former challenge-jail SET_INTERPRETER/SET_RPATH settings.
RUN patchelf --set-interpreter /home/user/libs/ld-linux-x86-64.so.2 --set-rpath /home/user/libs run

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
WORKDIR /home/user
COPY --from=app --chmod=0555 /app/run ./chall
COPY --from=app /lib/x86_64-linux-gnu ./libs

EXPOSE 1337
ENV TIMEOUT=120
USER user
CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} ./chall,stderr\""]
