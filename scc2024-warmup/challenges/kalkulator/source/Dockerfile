FROM python:3.12-slim-bookworm
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
WORKDIR /home/user
COPY --chmod=0555 kalkulator.py ./chall
COPY flag.txt ./
EXPOSE 1337
ENV TIMEOUT=120
ENV PYTHONUNBUFFERED=1
USER user
CMD ["sh", "-c", "exec socat TCP-LISTEN:1337,reuseaddr,fork \"EXEC:timeout ${TIMEOUT} ./chall,stderr\""]
