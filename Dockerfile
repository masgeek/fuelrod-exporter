# Base image for API and Worker
FROM python:3.13.0a6-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- COPY FILES FIRST ----
COPY pyproject.toml /app/
COPY poetry.lock /app/
COPY README.md /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install latest Poetry 2.x
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry


# ---- Install dependencies ----
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

RUN mkdir -p /app/exports && chmod 777 /app/exports

RUN mkdir -p /app/logs && chmod 777 /app/logs
