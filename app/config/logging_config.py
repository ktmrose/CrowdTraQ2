import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

def setup_logging(
    level: int = logging.INFO,
    to_stdout: bool = True,
    to_file: bool = False,
    file_path: str | None = None,
    max_bytes: int = 5_000_000,  # ~5MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Configure the root 'app' logger with optional stdout and rotating file handlers.
    Safe to call multiple times; it clears duplicate handlers.
    """
    logger = logging.getLogger("app")
    logger.setLevel(level)
    logger.propagate = False  # prevent duplicate logs via root logger
    logger.handlers.clear()

    formatter = logging.Formatter(DEFAULT_FORMAT)

    if to_stdout:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        sh.setLevel(level)
        logger.addHandler(sh)

    if to_file:
        if not file_path:
            # Default logs directory under project
            logs_dir = Path.cwd() / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            file_path = str(logs_dir / "server.log")

        fh = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        logger.addHandler(fh)

    return logger