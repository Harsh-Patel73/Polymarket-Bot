import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """Configure rotating file + console logging. Returns the root bot logger."""
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("polybot")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    # Console
    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    logger.addHandler(console)

    # Rotating file: 10 MB per file, keep 5 backups
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "bot.log"),
        maxBytes=10_000_000,
        backupCount=5,
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        )
    )
    logger.addHandler(file_handler)

    return logger
