FROM python:3.12-alpine

WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy application files
COPY / /app/

# Expose port
EXPOSE 8000

# Start supervisord
CMD ["/app/docker-entrypoint.sh"]
