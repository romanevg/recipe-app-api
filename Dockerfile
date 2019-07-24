FROM python:3.7-alpine

# It tells Python to run in unbuffered mode which is recommended when running Python within Docker containers. The reason for this is that it doesn't allow Python to buffer the outputs. It just prints them directly. And this avoids some complications and things like that with the Docker image when you're running your python application.
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
