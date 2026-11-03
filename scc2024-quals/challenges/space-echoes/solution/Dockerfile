FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir scapy==2.6.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# capture.pcapng is mounted into the working directory by the test runner.
# The solver reassembles the TCP streams, extracts the plaintext/base64
# flag parts and prints the assembled flag for the grep check below.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
