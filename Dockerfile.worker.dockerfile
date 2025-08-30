FROM masgeek/fuelrod-exporter-base AS worker

WORKDIR /app

# Copy application code (only here, not in base)
COPY src /app/src

# Copy supervisor config for worker
COPY supervisord_worker.conf /etc/supervisor/conf.d/supervisord.conf

# Environment variables for Dramatiq
ENV REDIS_URL=redis://redis:6379/0
ENV DRAMATIQ_PROCESSES=1
ENV DRAMATIQ_THREADS=2

# Start supervisord to manage Dramatiq worker
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
