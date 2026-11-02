FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir requests==2.32.3
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
