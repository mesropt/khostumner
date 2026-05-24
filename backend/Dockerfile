FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt -r requirements-dev.txt

COPY . .

EXPOSE 8000
