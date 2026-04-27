from __future__ import annotations

import logging
from urllib.parse import urlparse

from app.config import settings
from app.scraping.browser import BrowserConfig, fetch_page_html
from app.scraping.fbref_mapping import map_fbref_match_to_db, map_fbref_stat_to_db
from app.scraping.fbref_parsers import (
    parse_fbref_match_payload,
    parse_fbref_player_match_stats,
    parse_fbref_player_per_90,
)
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "fbref-page"
    return slugify(path.split("/")[-1])


def scrape_fbref_page(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    runtime_slug = slug or _slug_from_url(url)
    context = {"source": "fbref", "slug": runtime_slug, "url": url, "headless": headless}
    log_event(logger, logging.INFO, "scrape.start", **context)
    try:
        html = fetch_page_html(url, BrowserConfig(headless=headless), source="fbref", slug=runtime_slug)
        raw_path = save_raw_html(runtime_slug, html, directory=settings.fbref_raw_data_dir)
        log_event(logger, logging.INFO, "scrape.raw_saved", raw_html_path=raw_path, html_length=len(html), **context)

        match_payload = parse_fbref_match_payload(html, url)
        player_match_stats = parse_fbref_player_match_stats(html, url)
        player_per_90 = parse_fbref_player_per_90(html, url)
        db_mapping = {
            "match": map_fbref_match_to_db(match_payload),
            "stats": [map_fbref_stat_to_db(row) for row in player_match_stats],
        }
        log_event(
            logger,
            logging.INFO,
            "scrape.records_extracted",
            match_found=bool(match_payload.get("external_id") or match_payload.get("title")),
            player_match_stats_count=len(player_match_stats),
            per90_count=len(player_per_90),
            db_match_write_attempted=bool(db_mapping.get("match")),
            db_stat_write_attempted=len(db_mapping.get("stats", [])),
            **context,
        )
        log_event(
            logger,
            logging.INFO,
            "db.write.result",
            target="db_mapping_preview",
            match_rows=1 if db_mapping.get("match") else 0,
            stat_rows=len(db_mapping.get("stats", [])),
            persisted=False,
            **context,
        )
        if not player_match_stats and not player_per_90:
            log_event(logger, logging.WARNING, "scrape.empty_result", match_found=bool(match_payload.get("external_id") or match_payload.get("title")), player_match_stats_count=0, per90_count=0, **context)

        payload = {
            "match": match_payload,
            "player_match_stats": player_match_stats,
            "player_per_90": player_per_90,
            "db_mapping": db_mapping,
        }
        parsed_path = save_parsed_payload(runtime_slug, payload, directory=settings.fbref_parsed_data_dir)
        log_event(logger, logging.INFO, "scrape.parsed_saved", parsed_data_path=parsed_path, **context)
        log_event(logger, logging.INFO, "scrape.success", parsed_data_path=parsed_path, raw_html_path=raw_path, **context)

        return {
            "slug": runtime_slug,
            "raw_html_path": raw_path,
            "parsed_data_path": parsed_path,
            "payload": payload,
        }
    except Exception as exc:
        log_exception(logger, "scrape.failed", exc, stage="fbref_pipeline", **context)
        raise
