FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir httpx==0.28.1
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
EXPOSE 8080
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py \"$SERVICE_WEB_HTTP_ENDPOINT\" > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
