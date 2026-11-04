FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir requests pillow numpy
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# source/images (the 256 reference meme images) is bind-mounted in at
# test time (see challenge.yaml's test[0].mounts) under /mounts/images.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python solve.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_flag\" /tmp/out"]
