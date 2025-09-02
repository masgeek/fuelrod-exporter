# fuelrod_exporter/scripts/worker.py

import subprocess
import sys
import signal
from fuelrod_exporter.core.logging import SharedLogger

logger = SharedLogger().get_logger()

def handle_signal(signum, frame):
    logger.info(f"🛑 Received signal {signum}. Terminating Dramatiq worker...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("🚀 Starting Dramatiq worker: fuelrod_exporter.tasks")
    try:
        subprocess.run([
            "dramatiq",
            "fuelrod_exporter.tasks",
            "--processes", "1",
            "--threads", "1"
        ])
    except KeyboardInterrupt:
        logger.info("🛑 Dramatiq worker interrupted by user. Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Dramatiq worker failed: {e}")
        sys.exit(1)