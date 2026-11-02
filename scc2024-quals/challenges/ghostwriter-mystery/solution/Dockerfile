FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tshark && \
    rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY keyboard.py ./
# Extraction command from the challenge README, then the solver script on the mounted capture.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "tshark -r /inputs/ghostwriter.pcap -Y '(usb.src == \"1.16.1\")' -T fields -e usbhid.data | sed 's/../:&/g2' > /tmp/commands.txt && python keyboard.py /tmp/commands.txt > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
