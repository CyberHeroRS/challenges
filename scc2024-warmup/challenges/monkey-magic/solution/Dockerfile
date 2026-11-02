FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pillow==11.0.0 pytesseract==0.3.13
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# The corrupted JPEG (first 12 header bytes zeroed out) is bind-mounted in at
# /solution/monkey_magic.jpg by the test runner. solve.py restores the
# standard FF D8 FF E0 ... JFIF prefix, OCRs the rendered flag text out of the
# repaired image (upscaled, same trick as waffles/secret-archives), and
# compares it against $flag_main, exiting non-zero on mismatch.
CMD ["python", "solve.py"]
