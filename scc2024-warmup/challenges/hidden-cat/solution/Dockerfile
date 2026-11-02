FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pillow==11.0.0 pytesseract==0.3.13
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# hidden_cat.png is bind-mounted in by the test runner at /solution/hidden_cat.png.
# solve.py recovers the flag text baked into the LSBs of the R/G/B channels
# (majority vote across the three channels cancels the per-channel dither
# noise), OCRs the resulting bitmap and compares the closest read against
# $flag_main, exiting non-zero on mismatch.
CMD ["python", "solve.py"]
