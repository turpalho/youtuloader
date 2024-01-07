FROM python:3.11-slim-buster

ENV BOT_NAME=$BOT_NAME
WORKDIR /usr/src/app/"${BOT_NAME}"

RUN apt-get update -y && apt-get install -y gcc ffmpeg

COPY requirements.txt /usr/src/app/"${BOT_NAME}"
RUN pip install --upgrade pip
RUN pip install -r /usr/src/app/"${BOT_NAME}"/requirements.txt

COPY . /usr/src/app/"${BOT_NAME}"