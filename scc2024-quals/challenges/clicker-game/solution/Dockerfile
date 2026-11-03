FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# The APK is mounted at /solution/clicker_game.apk by the test runner.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
