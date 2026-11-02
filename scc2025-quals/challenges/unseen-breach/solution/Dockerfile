FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir scapy==2.6.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solv.py ./
# capture.pcapng is mounted at runtime (see challenge.yaml test.mounts) next to solv.py.
# solv.py reassembles the TCP streams with scapy, extracts the injected shell
# payload from the vulnerable /api/verify endpoint, RC4-decrypts the
# exfiltrated flag.txt using the key captured in the same stream, and prints
# it as "FLAG: <flag>". Passes only when the solver exits cleanly and that
# line contains the expected flag.
CMD ["sh", "-c", "python solv.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
