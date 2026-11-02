FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY exploit.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python exploit.py REMOTE HOST=$SERVICE_APP_MAIN_HOST PORT=$SERVICE_APP_MAIN_PORT FLAG=$flag_main > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
