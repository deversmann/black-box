"""Structured JSON logging infrastructure for Black Box Swarm."""

import json
import logging
import logging.handlers
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""

    # Patterns for sensitive data redaction
    SENSITIVE_PATTERNS = [
        (re.compile(r'(api[_-]?key["\s:=]+)([^\s"]+)', re.IGNORECASE), r'\1REDACTED'),
        (re.compile(r'(password["\s:=]+)([^\s"]+)', re.IGNORECASE), r'\1REDACTED'),
        (re.compile(r'(Bearer\s+)([^\s"]+)', re.IGNORECASE), r'\1REDACTED'),
        (re.compile(r'(token["\s:=]+)([^\s"]+)', re.IGNORECASE), r'\1REDACTED'),
    ]

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record
        """
        # Build base log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add event_type if present in extra
        if hasattr(record, "event_type"):
            log_entry["event_type"] = record.event_type

        # Add data dict if present in extra
        if hasattr(record, "data"):
            log_entry["data"] = record.data

        # Add correlation_id if present in extra
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Convert to JSON
        json_str = json.dumps(log_entry, default=str)

        # Redact sensitive data
        json_str = redact_sensitive_data(json_str)

        return json_str


def redact_sensitive_data(text: str) -> str:
    """Redact sensitive information from text.

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive data replaced with REDACTED
    """
    for pattern, replacement in JSONFormatter.SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def configure_logging(config: Any) -> None:
    """Configure logging from application config.

    Args:
        config: Application configuration object with logging settings
    """
    # Get logging configuration
    log_config = config.logging
    level_str = log_config.get("level", "INFO")
    output = log_config.get("output", "stdout")
    log_file = log_config.get("file", "./logs/swarm.log")

    # Get rotation config (with defaults)
    rotation_config = log_config.get("rotation", {})
    max_bytes = rotation_config.get("max_bytes", 10 * 1024 * 1024)  # 10MB default
    backup_count = rotation_config.get("backup_count", 5)

    # Parse log level
    level = getattr(logging, level_str.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger("blackbox")
    root_logger.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create JSON formatter
    formatter = JSONFormatter()

    # Add handlers based on output config
    if output in ("stdout", "both"):
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if output in ("file", "both"):
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Log that logging is configured
    root_logger.info(
        "Logging system initialized",
        extra={
            "event_type": "logging_initialized",
            "data": {
                "level": level_str,
                "output": output,
                "file": log_file if output in ("file", "both") else None,
                "max_bytes": max_bytes,
                "backup_count": backup_count,
            },
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (e.g., "blackbox.agents.command")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
