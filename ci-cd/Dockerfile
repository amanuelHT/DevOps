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
RUN python -m compileall . \
    && mkdir -p bytecode \
    && mv __pycache__/*.pyc bytecode/ \
    && rm -rf __pycache__ \
    && find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# 3. Copy installed packages & executables
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 4. Copy only compiled bytecode files
COPY --from=builder /app/bytecode/app.cpython-312.pyc      /app/app.pyc
COPY --from=builder /app/bytecode/config.cpython-312.pyc   /app/config.pyc
COPY --from=builder /app/bytecode/database.cpython-312.pyc /app/database.pyc
COPY --from=builder /app/bytecode/wsgi.cpython-312.pyc     /app/wsgi.pyc

# 5. Copy static assets
COPY --from=builder /app/static      /app/static
COPY --from=builder /app/templates   /app/templates
COPY --from=builder /app/image_pool  /app/image_pool

# 6. Non-root user
RUN useradd -u 1001 -m flaskuser
USER 1001


# 7. Expose port & launch via Gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
