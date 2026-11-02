FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
        hashcat \
        pocl-opencl-icd \
        ocl-icd-libopencl1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir Faker~=37.1 requests~=2.32
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY check.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python check.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
