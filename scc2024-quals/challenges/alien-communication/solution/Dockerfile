FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir sstv==0.2.0 numpy==2.2.0 scipy==1.14.1 pillow==11.0.0 pytesseract==0.3.13
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# The wav is bind-mounted in at /solution/alien_communication.wav by the test
# runner. solve.py decodes the SSTV picture hidden in the audio, OCRs the
# flag text drawn on the TV screen (upscaled + thresholded, several variants
# per line, same leetspeak-OCR trick as secret-archives) and compares the
# closest read against $flag_main, exiting non-zero on mismatch.
CMD ["python", "solve.py"]
