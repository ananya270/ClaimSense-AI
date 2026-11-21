"""Centralized logging configuration for ClaimSense AI (Production Hardened)."""
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Formats log records as structured JSON lines (JSONL)."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request context if present
        for attr in ("request_id", "user_id", "claim_id", "event", "duration_ms", "method", "path"):
            if hasattr(record, attr):
                log_obj[attr] = getattr(record, attr)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger(
    name: str = "claimsense",
    level: Optional[int] = None,
    use_json: Optional[bool] = None,
) -> logging.Logger:
    """Configures and returns a standardized logger.

    If use_json is True (or JSON_LOGGING environment variable is enabled),
    formats log entries as structured JSON lines.
    """
    logger = logging.getLogger(name)

    if use_json is None:
        use_json = os.getenv("JSON_LOGGING", "false").strip().lower() in ("true", "1", "yes")

    target_level = level or logging.INFO
    logger.setLevel(target_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(target_level)

        if use_json:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_rotating_file_handler(
    logger: logging.Logger,
    log_file_path: Path,
    max_bytes: int = 50 * 1024 * 1024,
    backup_count: int = 10,
    use_json: bool = False,
) -> None:
    """Attaches a rotating file handler to the specified logger."""
    from logging.handlers import RotatingFileHandler

    log_file_path = Path(log_file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    if use_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    logger.addHandler(handler)
