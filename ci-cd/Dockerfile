# ─── STAGE 1: BUILDER ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# 1. Copy & install wheels (offline) + requirements
COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# 2. Copy in source & compile to bytecode
COPY app/ .
RUN python -m compileall .

# 3. Remove all .py files so only bytecode remains
RUN find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# 4. Copy in installed packages & compiled bytecode + static assets
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin     /usr/local/bin
COPY --from=builder /app/__pycache__   /app/__pycache__
COPY --from=builder /app/static        /app/static
COPY --from=builder /app/templates     /app/templates
COPY --from=builder /app/image_pool    /app/image_pool

# 5. Create and switch to non-root user
RUN useradd -u 1001 -m flaskuser
USER 1001

# 6. Expose port and launch Gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
