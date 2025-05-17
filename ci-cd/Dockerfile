FROM python:3.12-slim AS builder
WORKDIR /src

# install deps
COPY ci-cd/wheels/    ./wheels/
COPY app/requirements.txt .
RUN pip install \
      --no-index \
      --no-cache-dir \
      --find-links=./wheels \
      -r requirements.txt

# compile & strip source
COPY app/ .
RUN python -m compileall . \
 && mkdir bytecode \
 && mv __pycache__/*.pyc bytecode/ \
 && rm -rf __pycache__ \
 && find . -type f -name '*.py' -delete
FROM python:3.12-slim
WORKDIR /app

# bring in only what we need
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/                          /usr/local/bin/
COPY --from=builder /src/bytecode/app.cpython-312.pyc       ./app.pyc
COPY --from=builder /src/bytecode/config.cpython-312.pyc    ./config.pyc
COPY --from=builder /src/bytecode/database.cpython-312.pyc  ./database.pyc
COPY --from=builder /src/static/       ./static/
COPY --from=builder /src/templates/    ./templates/
COPY --from=builder /src/image_pool/   ./image_pool/

# non-root user
RUN useradd -u 1001 -m flaskuser && chown -R flaskuser:flaskuser /app
USER 1001

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
