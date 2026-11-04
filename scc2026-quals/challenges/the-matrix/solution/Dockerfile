FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir requests
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# Passes only when the solver exits cleanly and its output contains both expected flags.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_flag1\" /tmp/out && grep -qF \"$flag_flag2\" /tmp/out"]
