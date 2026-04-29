"""
Structured JSON logger for PlacementPro+ backend.

Every log entry is a single JSON object, making it trivially parseable
by log aggregators like ELK Stack, Datadog, or CloudWatch Logs.

Log format:
{
    "timestamp": "2026-04-24T10:00:00.000Z",
    "level": "INFO",
    "logger": "placementpro",
    "message": "...",
    "module": "routes",
    "correlation_id": "f47ac10b-58cc-..."   # unique per HTTP request
}
"""

import logging
import logging.handlers
import json
import os
import traceback
from datetime import datetime, timezone


# ─── JSON Formatter ───────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """
    Formats each log record as a compact JSON object on a single line.
    Keeps the 'correlation_id' field if it was added via the Flask g context.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level":     record.levelname,
            "logger":    record.name,
            "module":    record.module,
            "message":   record.getMessage(),
        }

        # Attach the per-request correlation ID if it was set
        if hasattr(record, "correlation_id"):
            payload["correlation_id"] = record.correlation_id

        # Attach exception info if present (full traceback as a string)
        if record.exc_info:
            payload["exception"] = traceback.format_exception(*record.exc_info)

        # Attach any extra kwargs passed to logger.info(..., extra={...})
        for key, val in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "correlation_id", "taskName",
            ) and not key.startswith("_"):
                payload[key] = val

        return json.dumps(payload, default=str)


# ─── Logger Factory ───────────────────────────────────────────────────────────

def get_logger(name: str = "placementpro") -> logging.Logger:
    """
    Returns a configured logger instance. Safe to call multiple times —
    handlers are only added once.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured — return the existing logger
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = JSONFormatter()

    # ── Console handler (always on) ───────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── Rotating file handler ─────────────────────────────────────────────────
    # Writes to backend/logs/app.log, keeps last 5 files × 5 MB each
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,   # 5 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent log records from propagating to the root logger (avoids duplicates)
    logger.propagate = False

    return logger


# ─── Correlation ID Filter ────────────────────────────────────────────────────

class CorrelationIdFilter(logging.Filter):
    """
    Injects the current request's correlation_id into every log record.
    The actual ID is pulled from Flask's 'g' context at emit time so it
    doesn't need to be passed explicitly to every log call.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            from flask import g
            record.correlation_id = getattr(g, "correlation_id", "no-request")
        except RuntimeError:
            # Outside of a Flask application context (e.g. during tests)
            record.correlation_id = "no-context"
        return True


def apply_correlation_filter(logger: logging.Logger) -> None:
    """Attach the CorrelationIdFilter to all handlers of the given logger."""
    f = CorrelationIdFilter()
    for handler in logger.handlers:
        handler.addFilter(f)


# ─── Module-level default logger ─────────────────────────────────────────────
logger = get_logger("placementpro")
apply_correlation_filter(logger)
