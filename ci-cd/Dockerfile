# Builder stage: install build dependencies and Python wheels
FROM python:3.12-slim AS builder
WORKDIR /src

# Install system packages needed to build Postgres client libraries
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from your wheelhouse
COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# Compile to bytecode and strip out sources
COPY app/ .
RUN python -m compileall . \
 && mkdir bytecode \
 && mv __pycache__/*.pyc bytecode/ \
 && rm -rf __pycache__ \
 && find . -type f -name '*.py' -delete

# Final stage: only runtime artifacts
FROM python:3.12-slim
WORKDIR /app

# Copy over installed packages and bytecode
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/                          /usr/local/bin/
COPY --from=builder /src/bytecode/app.cpython-312.pyc       ./app.pyc
COPY --from=builder /src/bytecode/config.cpython-312.pyc    ./config.pyc
COPY --from=builder /src/bytecode/database.cpython-312.pyc  ./database.pyc

# Static assets and the image pool
COPY --from=builder /src/static/       ./static/
COPY --from=builder /src/templates/    ./templates/
COPY --from=builder /src/image_pool/   ./image_pool/

# Ensure non-root user owns /app
RUN useradd -u 1001 -m flaskuser && chown -R flaskuser:flaskuser /app
USER 1001

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
