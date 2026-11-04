FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir sympy==1.13.3
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# output.txt is bind-mounted in at test time (see challenge.yaml's test[0].mounts).
# Passes only when the solver exits cleanly and its recovered flag matches the
# flag injected by the test runner via the flag_main environment variable.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
