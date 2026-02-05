FROM python:3.9-slim

RUN pip install flask

WORKDIR /usr/src/app

COPY /src .

EXPOSE 3500

CMD ["python", "server.py"]