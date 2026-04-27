from __future__ import annotations

import json
import logging
from pathlib import Path
import re

from app.config import settings
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "unknown-player"


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    log_event(logger, logging.DEBUG, "storage.ensure_directory", directory=str(directory))
    return directory


def save_raw_html(slug: str, html: str, directory: str | Path = settings.raw_data_dir) -> str:
    output_dir = ensure_directory(directory)
    output_path = output_dir / f"{slug}.html"
    log_event(logger, logging.INFO, "storage.write_raw.start", slug=slug, path=str(output_path), bytes=len(html.encode("utf-8")))
    try:
        output_path.write_text(html, encoding="utf-8")
    except Exception as exc:
        log_exception(logger, "storage.write.failed", exc, slug=slug, path=str(output_path), artifact_type="raw_html")
        raise
    log_event(logger, logging.INFO, "storage.write_raw.success", slug=slug, path=str(output_path), bytes=len(html.encode("utf-8")))
    return str(output_path)


def save_parsed_payload(slug: str, payload: dict[str, object], directory: str | Path = settings.parsed_data_dir) -> str:
    output_dir = ensure_directory(directory)
    output_path = output_dir / f"{slug}.json"
    payload_json = json.dumps(payload, indent=2, ensure_ascii=False)
    payload_keys = sorted(payload.keys()) if isinstance(payload, dict) else []
    log_event(logger, logging.INFO, "storage.write_parsed.start", slug=slug, path=str(output_path), bytes=len(payload_json.encode("utf-8")), payload_keys=payload_keys)
    try:
        output_path.write_text(payload_json, encoding="utf-8")
    except Exception as exc:
        log_exception(logger, "storage.write.failed", exc, slug=slug, path=str(output_path), artifact_type="parsed_json")
        raise
    log_event(logger, logging.INFO, "storage.write_parsed.success", slug=slug, path=str(output_path), bytes=len(payload_json.encode("utf-8")), payload_keys=payload_keys)
    return str(output_path)
