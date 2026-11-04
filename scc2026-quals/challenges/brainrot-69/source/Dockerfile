FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    busybox \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Pillow

WORKDIR /app

COPY images/ /app/images/
COPY encode.py /app/
COPY index.html /app/static/
COPY start.sh /app/

RUN chmod +x /app/start.sh

EXPOSE 80

CMD ["/app/start.sh"]
