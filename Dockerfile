FROM python:3.7-alpine
MAINTAINER Santosh

ENV PYTHONUNBUFFERED 1

COPY ./requirement.txt /requirement.txt
RUN pip install -r /requirement.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
