FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir httpx==0.28.1 flask==3.1.0
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py oracle_server.py ./
# The admin bot reaches the oracle on this runner's address; the solver polls it locally.
CMD ["sh", "-c", "python oracle_server.py >/tmp/oracle.log 2>&1 & export ORACLE_SERVER_URL=http://$(hostname -i | cut -d' ' -f1):9999; sleep 2; python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
