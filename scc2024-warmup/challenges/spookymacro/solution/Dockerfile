FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir oletools==0.60.2
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# secret.docm is bind-mounted in at test time (see challenge.yaml's
# test[0].mounts).
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
