FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pillow==11.0.0
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# art.png is bind-mounted in by the test runner at /solution/art.png.
# solve.py reads the four visible ciphers painted on the canvas (Morse code,
# Braille, a Brainfuck program and three color swatches), decodes each one
# from the real pixel data and reassembles the flag, exiting non-zero on any
# mismatch against $flag_main.
CMD ["python", "solve.py"]
