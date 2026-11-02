FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.15.0
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY analyze.py sol.py ./
# access.log is mounted in from public/ (see challenge.yaml test.mounts).
# analyze.py derives every answer (domain, attacker IP, browser/OS, sqlmap
# version, the winning SQLi payload, and the leaked file) straight from the
# log's own content and asserts real attack-pattern thresholds along the
# way; sol.py then plays the live Q&A service with those derived answers.
# Passes only when the solver exits cleanly and its output contains the
# expected flag the service printed back.
CMD ["sh", "-c", "python sol.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
