FROM python:latest

LABEL maintainer="InnovativeInventor"

RUN pip3 install flask
RUN pip3 install grip
RUN pip install -U pytest
RUN apt-get update && apt-get install -y \
    nano \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
