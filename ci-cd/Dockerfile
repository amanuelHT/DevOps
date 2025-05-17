# ─── STAGE 1: BUILDER ───────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /src

# 1. Copy & install wheels (offline) + requirements
COPY ci-cd/wheels/   ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# 2. Copy in all source and compile to bytecode
COPY app/ .
RUN python -m compileall . \
 && mkdir bytecode \
 && mv __pycache__/*.pyc bytecode/ \
 && rm -rf __pycache__ \
 && find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# 3. Copy in installed packages & compiled bytecode + static assets
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/                          /usr/local/bin/
COPY --from=builder /src/bytecode/app.cpython-312.pyc       ./app.pyc
COPY --from=builder /src/bytecode/config.cpython-312.pyc    ./config.pyc
COPY --from=builder /src/bytecode/database.cpython-312.pyc  ./database.pyc
COPY --from=builder /src/static/       ./static/
COPY --from=builder /src/templates/    ./templates/
COPY --from=builder /src/image_pool/   ./image_pool/

# 4. Create a numeric-only user & switch to it
RUN useradd -u 1001 -m flaskuser \
 && chown -R flaskuser:flaskuser /app
USER 1001

# 5. Expose & run via Gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
