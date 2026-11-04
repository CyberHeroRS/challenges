FROM python:3.9-slim-bullseye

WORKDIR /app


RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]