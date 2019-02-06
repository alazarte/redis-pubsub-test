FROM python:3

RUN pip install redis

COPY ./chat /opt/chat

WORKDIR "/opt/chat"

ENTRYPOINT ["python", "chat.py"]
