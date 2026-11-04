FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# secure-cipher is bind-mounted in at test time (see challenge.yaml's
# test[0].mounts) -- only needed for its ELF symbol table (rot_the_flag's
# address), never executed locally.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_flag\" /tmp/out"]
