"""Centralized logging configuration for ClaimSense AI."""
import logging
import sys
from typing import Optional


def setup_logger(name: str = "claimsense", level: Optional[int] = None) -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level or logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level or logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
