#!/bin/sh

cd /app

# Encode the flag
python3 encode.py

# Clean up source files
rm -rf /app/images /app/encode.py

# Serve the static directory
cd /app/static
exec busybox httpd -f -p 80
