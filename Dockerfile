FROM python:3

COPY ./src /app
COPY ./config /app/config

WORKDIR "/app"

ENTRYPOINT ["python", "main.py"]
