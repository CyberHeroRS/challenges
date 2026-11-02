FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pycryptodome==3.21.0 gmpy2==2.2.1 tqdm==4.67.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY rsa2m_solution.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python rsa2m_solution.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
