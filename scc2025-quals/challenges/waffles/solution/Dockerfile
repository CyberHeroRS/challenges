FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests==2.32.3 pillow==11.0.0 pytesseract==0.3.13
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# solve.py itself compares the OCR'd image text against $flag_main (with
# leetspeak-OCR-ambiguity normalization) and exits non-zero on mismatch.
CMD ["python", "solve.py"]
