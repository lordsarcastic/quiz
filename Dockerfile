# pull official base image
FROM python:3.9.13-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ARG DB_NAME
ARG DB_PASSWORD

RUN apt-get update \
    && apt-get -y install build-essential gcc python3-dev musl-dev \
    && apt-get -y install libffi-dev

# copy entire project directory
COPY . .

RUN pip install pipenv
RUN pipenv install --system

# clover is our default user
RUN adduser clover
USER clover
