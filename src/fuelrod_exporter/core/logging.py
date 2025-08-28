import sys
from loguru import logger
from colorama import init, Fore, Style


class SharedLogger:
    def __init__(self, log_file=None, level='INFO'):
        self.log_file = log_file
        self.level = level
        init(autoreset=True)  # Initialize Colorama
        self.configure_logger()

    def configure_logger(self):
        logger.remove()  # Remove default configuration

        # Configure logger to write to file if specified
        if self.log_file:
            logger.add(self.log_file, rotation='10 MB', level=self.level, colorize=False)

        # Always log to the console with color
        logger.add(
            sys.stdout,
            level=self.level,
            colorize=True,
            format=self.get_colored_format()
        )

    def get_colored_format(self):
        """Define colorized format using Colorama"""
        return (
            f"<green>{{time:YYYY-MM-DD HH:mm:ss}}</green> | "
            f"<level>{Fore.CYAN}{{level}}{Style.RESET_ALL}</level> | "
            f"<cyan>{{name}}</cyan>:<cyan>{{function}}</cyan>:<cyan>{{line}}</cyan> - "
            f"<level>{{message}}</level>"
        )

    def get_logger(self):
        return logger
