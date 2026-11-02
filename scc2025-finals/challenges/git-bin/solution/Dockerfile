FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir requests==2.32.3 beautifulsoup4==4.12.3
ENV GIT_AUTHOR_NAME=solver GIT_AUTHOR_EMAIL=solver@example.com GIT_COMMITTER_NAME=solver GIT_COMMITTER_EMAIL=solver@example.com
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY main.py get_object.py leak_file.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python main.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
