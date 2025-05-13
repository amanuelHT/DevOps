FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
COPY ci-cd/wheels/ ./wheels/

RUN pip install --no-index --no-cache-dir --find-links=./wheels -r requirements.txt

COPY app/ .
RUN useradd -u 1001 -m flaskuser
USER 1001


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
