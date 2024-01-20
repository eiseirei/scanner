FROM python:3.11
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && \
	pip install --upgrade pip && pip install -r requirements.txt && \
	apt-get install iputils-ping -y
RUN mkdir /app