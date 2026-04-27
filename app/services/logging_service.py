from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from app.config import settings


_CONFIGURED = False


class KeyValueFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ")
        event = getattr(record, "event", record.getMessage())
        fields = getattr(record, "fields", {}) or {}
        field_text = " ".join(f"{key}={_format_value(value)}" for key, value in sorted(fields.items()))
        message = f"{timestamp} {record.levelname} {record.name} {event}"
        if field_text:
            message = f"{message} {field_text}"
        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"
        return message


def _format_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\n", "\\n")
    if text == "":
        return '""'
    if any(char.isspace() for char in text) or any(char in text for char in ['"', "="]):
        return f'"{text.replace(chr(34), chr(92) + chr(34))}"'
    return text


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _resolve_level(level_name: str | None) -> int:
    if not level_name:
        return logging.INFO
    return getattr(logging, str(level_name).upper(), logging.INFO)


def configure_logging(force: bool = False) -> None:
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    root = logging.getLogger()
    if force:
        for handler in list(root.handlers):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    root.setLevel(_resolve_level(settings.log_level))

    formatter = KeyValueFormatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    if _coerce_bool(settings.log_file_enabled) and settings.log_file_path:
        try:
            log_path = Path(settings.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError:
            fallback_logger = logging.getLogger("app.logging")
            fallback_logger.warning(
                "file logging disabled due to path error",
                extra={
                    "event": "logging.file_handler_unavailable",
                    "fields": {"path": settings.log_file_path},
                },
                exc_info=True,
            )

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


def is_debug_enabled() -> bool:
    return _coerce_bool(settings.log_debug_enabled, default=False)


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    logger.log(level, event, extra={"event": event, "fields": fields})


def log_exception(logger: logging.Logger, event: str, exc: BaseException, **fields: Any) -> None:
    enriched_fields = {**fields, "error": type(exc).__name__, "message": str(exc)}
    logger.error(event, extra={"event": event, "fields": enriched_fields}, exc_info=(type(exc), exc, exc.__traceback__))
