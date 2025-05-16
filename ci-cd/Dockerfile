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

# 2. Copy in source, compile to bytecode
COPY app/ .
RUN python -m compileall .

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# 3. Bring in only what we need:
#    - Installed packages
#    - Compiled bytecode
#    - Static assets, templates, image pool, Startup.sh
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/__pycache__          /app/__pycache__
COPY --from=builder /app/static               /app/static
COPY --from=builder /app/templates            /app/templates
COPY --from=builder /app/image_pool           /app/image_pool
COPY --from=builder /app/Startup.sh           /app/Startup.sh

# 4. Create non-root user
RUN useradd -u 1001 -m flaskuser
USER flaskuser

# 5. Expose & launch via gunicorn
EXPOSE 5000
ENTRYPOINT ["./Startup.sh", "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
