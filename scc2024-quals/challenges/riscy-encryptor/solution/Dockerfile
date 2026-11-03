FROM python:3.12-slim-bookworm
WORKDIR /solution
COPY solve.py ./
# Passes only when the solver exits cleanly and recovers the real flag from enc.bin.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
