# ─── STAGE 1: BUILDER ──────────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /src

# 1) install wheels + requirements
COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# 2) copy source & compile to bytecode
COPY app/ .
RUN python -m compileall . \
 && mkdir bytecode \
 && mv __pycache__/*.pyc bytecode/ \
 && rm -rf __pycache__

# 3) delete every .py (so none will survive)
RUN find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ──────────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# 4) pull in only the compiled bytecode and static files
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /src/bytecode       /app
COPY --from=builder /src/static         /app/static
COPY --from=builder /src/templates      /app/templates
COPY --from=builder /src/image_pool     /app/image_pool

# non-root user
RUN useradd -u 1001 -m flaskuser && chown -R flaskuser:flaskuser /app
USER 1001



# 6) expose & run
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
