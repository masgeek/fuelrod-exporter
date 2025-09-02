from datetime import datetime, timedelta
from pathlib import Path

import dramatiq
from dateutil import tz

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.utils import format_size, format_age, parse_interval_to_seconds
from fuelrod_exporter.services.minio_service import MinioService
from fuelrod_exporter.worker_app import get_app

logger = SharedLogger().get_logger()
minio = MinioService()

SERVER_TZ = tz.gettz(Config.SERVER_TZ)  # e.g., "Africa/Nairobi"

app = get_app()


def log_minio_objects_only(cutoff: datetime):
    now = datetime.now(tz=SERVER_TZ)
    deleted = 0

    logger.info("🪣 MinIO Bucket Contents (local folder empty):")
    logger.info(f"{'File Name':<30} {'Modified':<20} {'Age':<10} {'Size':<10} {'Status'}")
    logger.info("-" * 100)

    try:
        objects = minio.list_objects()
        for obj in objects:
            if not obj.object_name.lower().endswith(tuple(Config.ALLOWED_EXTENSIONS)):
                continue


            modified = obj.last_modified
            if modified.tzinfo is None:
                modified = modified.replace(tzinfo=SERVER_TZ)

            age_seconds = int((now - modified).total_seconds())
            size = format_size(obj.size)
            status = "✅ Retained"

            if obj.object_name in Config.PROTECTED_FILES:
                status = "🔒 Skipped (protected)"
            elif modified < cutoff:
                try:
                    minio.remove_object(obj.object_name)
                    status = "🗑️ Deleted (MinIO only)"
                    deleted += 1
                except Exception as e:
                    status = f"⚠️ Failed: {e}"

            logger.info(
                f"{obj.object_name:<30} {modified.strftime('%Y-%m-%d %H:%M'):<20} {format_age(age_seconds):<10} {size:<10} {status}"
            )

        logger.info("-" * 100)
        logger.info(f"MinIO-only cleanup complete. {deleted} remote files deleted.")
    except Exception as e:
        logger.error(f"Failed to list MinIO objects: {e}")


@dramatiq.actor(store_results=False)
def cleanup_export_folder(directory: str, max_age_seconds: int = 3600):
    cutoff = datetime.now(tz=SERVER_TZ) - timedelta(seconds=max_age_seconds)
    now = datetime.now(tz=SERVER_TZ)
    deleted = 0
    path = Path(directory).resolve()

    if not path.exists() or not any(path.iterdir()):
        logger.warning(f"Export folder is missing or empty: {directory}")
        log_minio_objects_only(cutoff)
        return

    valid_files = [
        f for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in Config.ALLOWED_EXTENSIONS
    ]

    if not valid_files:
        logger.warning(f"Export folder is empty or has no valid files: {directory}")
        log_minio_objects_only(cutoff)
        return

    logger.info("📂 Export Folder Contents:")
    logger.info(f"{'File Name':<30} {'Modified':<20} {'Age':<10} {'Size':<10} {'Status'}")
    logger.info("-" * 100)

    for file in path.iterdir():
        if not file.is_file():
            continue

        if file.suffix.lower() not in Config.ALLOWED_EXTENSIONS:
            continue  # skip unsupported file types

        modified = datetime.fromtimestamp(file.stat().st_mtime, tz=SERVER_TZ)
        age_seconds = int((now - modified).total_seconds())
        size = format_size(file.stat().st_size)
        status = "✅ Retained"

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
