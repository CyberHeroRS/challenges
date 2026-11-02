FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir z3-solver==4.13.4.0
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY sol.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python sol.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
