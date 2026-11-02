FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
WORKDIR /home/user
COPY --chmod=0555 ./outer ./chall

EXPOSE 1337
ENV TIMEOUT=120
USER user
CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} ./chall,stderr\""]
