from datetime import datetime, timedelta
from pathlib import Path

import dramatiq

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.utils import format_size, format_age, parse_interval_to_seconds
from fuelrod_exporter.services.minio_service import MinioFileUploader
from fuelrod_exporter.worker_app import get_app

logger = SharedLogger().get_logger()
minio = MinioFileUploader()

app = get_app()


@dramatiq.actor(store_results=True)
def cleanup_export_folder(directory: str, max_age_seconds: int = 3600):
    cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
    now = datetime.now()
    deleted = 0
    path = Path(directory).resolve()

    if not path.exists():
        logger.warning(f"Export folder does not exist: {directory}")
        return

    logger.info("📂 Export Folder Contents:")
    logger.info(f"{'File Name':<30} {'Modified':<20} {'Age':<10} {'Size':<10} {'Status'}")
    logger.info("-" * 100)

    for file in path.iterdir():
        if not file.is_file():
            continue

        if file.suffix.lower() not in Config.ALLOWED_EXTENSIONS:
            continue  # skip unsupported file types

        modified = datetime.fromtimestamp(file.stat().st_mtime)
        age_seconds = int((now - modified).total_seconds())
        size = format_size(file.stat().st_size)
        status = ""

        if file.name in Config.PROTECTED_FILES:
            status = "🔒 Skipped (protected)"
        elif modified < cutoff:
            try:
                file.unlink()
                minio.remove_object(file.name)
                status = "🗑️ Deleted (local + MinIO)"
                deleted += 1
            except Exception as e:
                status = f"⚠️ Failed: {e}"
        else:
            status = "✅ Retained"

        logger.info(
            f"{file.name:<30} {modified.strftime('%Y-%m-%d %H:%M'):<20} {format_age(age_seconds):<10} {size:<10} {status}"
        )

    logger.info("-" * 100)
    logger.info(f"Cleanup complete. {deleted} files deleted from {directory} and MinIO")


def trigger_cleanup():
    with app.app_context():
        folder = Config.EXPORT_FOLDER
        max_age = parse_interval_to_seconds(Config.EXPORT_MAX_AGE)
        max_age_str = format_age(max_age)

        logger.info(f"Scheduler triggered cleanup task for folder: {folder} (max age: {max_age_str})")
        cleanup_export_folder.send(folder, max_age)
