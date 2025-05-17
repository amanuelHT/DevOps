# ─── STAGE 1: BUILDER ───────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /app

# 1. Install wheels + requirements
COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# 2. Copy in source, compile, delete sources
COPY app/ .
RUN python -m compileall . \
 && find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# 3. Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 4. Copy compiled bytecode + assets
COPY --from=builder /app/__pycache__ /app/__pycache__
COPY --from=builder /app/static     /app/static
COPY --from=builder /app/templates  /app/templates
COPY --from=builder /app/image_pool /app/image_pool
COPY --from=builder /app/database_file /app/database_file

# 5. Non-root user
RUN useradd -u 1001 -m flaskuser
USER 1001


# 6. Expose & run Gunicorn on app:app
EXPOSE 5000
CMD ["gunicorn","--bind","0.0.0.0:5000","app:app"]
