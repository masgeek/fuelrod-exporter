# Use a lightweight official Python base image
FROM python:3.13-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
        supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -sf /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy only dependency files for caching
COPY pyproject.toml poetry.lock* README.md /app/

# Configure Poetry and install dependencies (no dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --without dev

# Create a non-root user
RUN useradd -ms /bin/bash fuelrod \
    && chown -R fuelrod:fuelrod /app

# Copy application source and configs
COPY . /app

# Create logs directory (with safer permissions)
RUN mkdir -p /app/logs \
    && chown -R fuelrod:fuelrod /app/logs

# Copy supervisord config
COPY supervisord_worker.conf /etc/supervisor/conf.d/supervisord.conf

# Switch to non-root user
USER fuelrod

# Expose logs to Docker stdout/stderr (optional)
VOLUME ["/app/logs"]

# Start supervisord to manage the Dramatiq worker
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
