FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    busybox \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Pillow

WORKDIR /app

COPY encode.py .
COPY gesture_LEFT.gif .
COPY gesture_RIGHT.gif .
COPY bosnov-67.wav .
COPY index.html .
COPY start.sh .

RUN chmod +x start.sh

RUN mkdir -p /app/static

EXPOSE 80

CMD ["/app/start.sh"]
