FROM debian:bullseye-slim
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends dosbox python3 socat && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
COPY --chmod=0555 piton.py /home/user/chall
COPY a /home/user/a
COPY b /home/user/b
COPY dosbox.conf /home/user/
WORKDIR /home/user
EXPOSE 9198
USER user
CMD ["socat", "TCP-LISTEN:9198,reuseaddr,fork", "EXEC:/home/user/chall,stderr"]
