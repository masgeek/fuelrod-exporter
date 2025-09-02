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
        bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -sf /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy dependency files for caching
COPY pyproject.toml poetry.lock* README.md /app/

# Configure Poetry and install dependencies (no dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --without dev

# Create non-root user
RUN useradd -ms /bin/bash fuelrod \
    && chown -R fuelrod:fuelrod /app

# Copy app source
COPY . /app

# Create logs and exports directories
RUN mkdir -p /app/logs /app/exports \
    && chown -R fuelrod:fuelrod /app/logs /app/exports

# Copy Supervisor config and start script
COPY ./supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY ./supervisor/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Declare volumes
VOLUME ["/app/logs", "/app/exports"]

# Switch to non-root user
USER fuelrod

# Start services via Supervisor (includes Dramatiq)
CMD ["/usr/local/bin/start.sh"]
