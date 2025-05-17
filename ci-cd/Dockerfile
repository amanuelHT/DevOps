# ─── STAGE 1: BUILDER ───────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /app

COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install --no-index --no-cache-dir --find-links=./wheels -r requirements.txt

COPY app/ .
RUN python -m compileall . \
 && mkdir -p bytecode \
 && mv __pycache__/*.pyc bytecode/ \
 && rm -rf __pycache__ \
 && find . -type f -name '*.py' -delete

# ─── STAGE 2: RUNTIME ───────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# 1) copy libraries
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# 2) copy only bytecode
COPY --from=builder /app/bytecode/app.cpython-312.pyc     /app/app.pyc
COPY --from=builder /app/bytecode/config.cpython-312.pyc  /app/config.pyc
COPY --from=builder /app/bytecode/database.cpython-312.pyc /app/database.pyc
COPY --from=builder /app/bytecode/wsgi.cpython-312.pyc    /app/wsgi.pyc

# copy static & templates
COPY --from=builder /app/static    /app/static
COPY --from=builder /app/templates /app/templates
COPY --from=builder /app/image_pool /app/image_pool

RUN useradd -u 1001 -m flaskuser
USER 1001

EXPOSE 5000
# now point Gunicorn at the compiled wsgi module:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
