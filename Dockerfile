FROM python:3

RUN pip install redis

COPY ./src /app
COPY ./config /app/config

WORKDIR "/app"

ENTRYPOINT ["python", "main.py"]
