FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir scapy==2.6.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# chall.pcap is mounted at runtime (see challenge.yaml test.mounts) next to solve.py.
# solve.py reassembles the FTP control channel with scapy to recover the
# plaintext credentials and the EPSV data-port used for each RETR'd file,
# then reassembles the secret.txt data channel and hex-decodes the flag it
# contains. Passes only when the solver exits cleanly and that line contains
# the expected flag.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
