FROM python:3.12.3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 7890
EXPOSE 8081