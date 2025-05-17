# ─── STAGE 1: BUILDER ───────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /src

# 1) Install wheels & requirements (offline)
COPY ci-cd/wheels/ wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# 2) Copy source + wsgi entrypoint
COPY app/     app/
COPY wsgi.py  wsgi.py

# 3) Compile everything to .pyc, then delete all .py
RUN python -m compileall app wsgi.py \
 && mkdir -p build/bytecode \
 && find app wsgi.py -type f -name '*.pyc' -exec mv {} build/bytecode/ \; \
 && find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# 4) Copy installed packages + executables
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 5) Copy bytecode & assets
COPY --from=builder /src/build/bytecode    /app/
COPY --from=builder /src/app/static        /app/static
COPY --from=builder /src/app/templates     /app/templates
COPY --from=builder /src/app/image_pool    /app/image_pool

# 6) Drop to non-root
RUN useradd -u 1001 -m flaskuser \
 && chown -R flaskuser:flaskuser /app
USER flaskuser

# 7) Expose + launch Gunicorn against the compiled bytecode
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
