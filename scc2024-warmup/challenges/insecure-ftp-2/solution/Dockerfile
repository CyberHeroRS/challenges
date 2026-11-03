FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir scapy==2.6.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# chall.pcap is mounted at runtime (see challenge.yaml test.mounts, which
# points at insecure-ftp-1's copy of the shared capture) next to solve.py.
# solve.py reassembles the FTP data channel that carried images/flag.png,
# verifies it against the known-good SHA-256 of that artifact, and reports
# the verified reading of its handwritten banner. Passes only when the
# solver exits cleanly and that line contains the expected flag.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
