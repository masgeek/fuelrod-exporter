from pathlib import Path
from datetime import datetime, timedelta
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.worker_app import get_app as current_app
from fuelrod_exporter.config import Config
import dramatiq
import os

logger = SharedLogger().get_logger()

PROTECTED_FILES = {".gitignore"}


@dramatiq.actor(store_results=True)
def cleanup_export_folder(directory: str, max_age_minutes: int = 60):
    cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
    deleted = 0
    path = Path(directory).resolve()

    if not path.exists():
        logger.warning(f"Export folder does not exist: {directory}")
        return

    # 🧾 Header
    logger.info("📂 Export Folder Contents:")
    logger.info(f"{'File Name':<30} {'Modified':<25} {'Status'}")
    logger.info("-" * 70)

    for file in path.iterdir():
        modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        status = ""

        if file.name in PROTECTED_FILES:
            status = "🔒 Skipped (protected)"
        elif file.is_file() and file.stat().st_mtime < cutoff.timestamp():
            try:
                file.unlink()
                status = "🗑️ Deleted"
                deleted += 1
            except Exception as e:
                status = f"⚠️ Failed: {e}"
        else:
            status = "✅ Retained"

        logger.info(f"{file.name:<30} {modified:<25} {status}")

    logger.info("-" * 70)
    logger.info(f"Cleanup complete. {deleted} files deleted from {directory}")

def trigger_cleanup():
    folder = Config.EXPORT_FOLDER
    max_age = Config.EXPORT_MAX_AGE

    logger.info(f"Scheduler triggered cleanup task for folder: {folder} (max age: {max_age} mins)")
    cleanup_export_folder.send(folder, max_age)
