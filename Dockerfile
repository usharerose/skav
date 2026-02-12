FROM python:3.10-alpine

LABEL maintainer="Chaojie Yan <ushareroses@gmail.com>"

# Setup basic Linux packages
RUN apk update && \
    apk add --no-cache \
    tini \
    build-base && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app/vibehist

COPY . .

# install dependencies
RUN python -m pip install --no-cache --upgrade pip && \
    python -m pip install --no-cache poetry==${POETRY_VERSION} && \
    poetry install && \
    find /usr/local/ -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

ENTRYPOINT ["/sbin/tini", "--"]
