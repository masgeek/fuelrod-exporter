# Use an official Python base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy only poetry files first for caching
COPY pyproject.toml poetry.lock* README.md /app/

# Install dependencies
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root --without dev
#RUN poetry install --no-interaction --no-root

# Copy source + configs
COPY . /app

# Create logs dir
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Default API command
CMD [ "python3", "src/run.py"]
#CMD ["gunicorn", "-c", "src/gunicorn.conf.py", "wsgi:app", "--chdir", "src"]
