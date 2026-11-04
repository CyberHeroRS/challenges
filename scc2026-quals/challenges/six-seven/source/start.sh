#!/bin/bash
set -e

echo "Generating video..."
python3 /app/encode.py

echo "Cleaning up..."
rm -f /app/encode.py /app/*.gif /app/*.wav /app/start.sh

echo "Starting web server..."
cd /app/static
cp /app/index.html .
rm -f /app/index.html
busybox httpd -f -p 80
