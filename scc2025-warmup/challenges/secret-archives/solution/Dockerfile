FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pillow==11.0.0 pytesseract==0.3.13
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# The docx (a zip archive) is bind-mounted in at /solution/challenge.docx by
# the test runner. solve.py extracts word/media/*.png, OCRs each candidate
# image (upscaled + thresholded, same leetspeak-OCR trick as waffles) and
# compares the closest read against $flag_main, exiting non-zero on mismatch.
CMD ["python", "solve.py"]
