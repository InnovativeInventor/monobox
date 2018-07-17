FROM python:latest

LABEL maintainer="InnovativeInventor"

RUN echo "Hello, world!" > /etc/motd
RUN echo "cat /etc/motd" > /etc/bash.bashrc

EXPOSE 6419
