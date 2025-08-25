import sys

from loguru import logger


class SharedLogger:
    def __init__(self, log_file=None, level='INFO'):
        self.log_file = log_file
        self.level = level
        self.configure_logger()

    def configure_logger(self):
        logger.remove()  # Remove default configuration

        # Configure logger to write to file if specified
        if self.log_file:
            logger.add(self.log_file, rotation='10 MB', level=self.level)

        # Always log to the console
        logger.add(sys.stdout, level=self.level)

    def get_logger(self):
        return logger

    def __repr__(self):
        return f'SharedLogger(log_file={self.log_file}, level={self.level})'
