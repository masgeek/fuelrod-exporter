import sys
import os

from dotenv import load_dotenv
from loguru import logger
from colorama import init

load_dotenv(verbose=True)


class SharedLogger:
    _configured = False  # ensure logger is only configured once

    def __init__(self):
        self.log_dir = os.getenv("LOG_DIR", "logs")
        self.level = os.getenv("LOG_LEVEL", "INFO")
        self.retention = os.getenv("LOG_RETENTION", "7 days")
        self.enable_file_logs = os.getenv("ENABLE_FILE_LOGS", "true").lower() == "true"
        init(autoreset=True)

        if not SharedLogger._configured:
            self._configure_logger()
            SharedLogger._configured = True

    def _configure_logger(self):
        logger.remove()
        os.makedirs(self.log_dir, exist_ok=True)

        if self.enable_file_logs:
            # All logs
            all_path = os.path.join(self.log_dir, "fuelrod_{time:YYYY-MM-DD}.log")
            logger.add(
                all_path,
                level=self.level,
                rotation="00:00",  # rotate daily
                retention=self.retention,
                enqueue=True,
            )

            # Error and above
            # error_path = os.path.join(self.log_dir, "error_{time:YYYY-MM-DD}.log")
            # logger.add(
            #     error_path,
            #     level="ERROR",
            #     rotation="00:00",
            #     retention=self.retention,
            #     enqueue=True,
            # )
            # critical_path = os.path.join(self.log_dir, "critical_{time:YYYY-MM-DD}.log")
            # logger.add(
            #     critical_path,
            #     level="CRITICAL",
            #     rotation="00:00",
            #     retention=self.retention,
            #     enqueue=True,
            # )

        # Console logs (always)
        logger.add(
            sys.stdout,
            level=self.level,
            colorize=True,
            # format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
            #        "| <level>{level:<8}</level> "
            #        "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            #        "<level>{message}</level>",
        )

    def get_logger(self):
        return logger
