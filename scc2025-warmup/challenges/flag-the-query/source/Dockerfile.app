FROM python:3.9

WORKDIR /app

COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

EXPOSE 1331

CMD ["python3", "app.py"]
