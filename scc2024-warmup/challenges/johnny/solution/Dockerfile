FROM kalilinux/kali-rolling
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends fcrackzip unzip wordlists ca-certificates && \
    gunzip -f /usr/share/wordlists/rockyou.txt.gz && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /solution
COPY johnny.zip solve.sh ./
RUN chmod +x solve.sh
# The flag is only inside flag.txt once the real ZIP password is cracked from
# rockyou.txt, so the runner passes when the solver exits cleanly and the
# recovered flag.txt contents match the flag injected by the test runner via
# the flag_main environment variable.
CMD ["sh", "-c", "./solve.sh > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
