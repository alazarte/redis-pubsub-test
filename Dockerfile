FROM python:3

RUN pip install redis

COPY ./app.py /opt/app.py

WORKDIR "/opt"

ENTRYPOINT ["python", "app.py"]
