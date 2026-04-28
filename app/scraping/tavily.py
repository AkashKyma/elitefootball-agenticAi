from __future__ import annotations

import logging
import re
from typing import Any

import requests

from app.config import settings
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)
_TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_ALLOWED_DOMAINS = ("transfermarkt.com", "fbref.com", "sofascore.com", "whoscored.com")


def classify_source_url(url: str) -> dict[str, str | bool]:
    normalized = str(url or "").strip()
    lowered = normalized.lower()
    if "transfermarkt.com" in lowered:
        if "/kader/" in lowered:
            return {
                "source_type": "transfermarkt_squad",
                "source_name": "transfermarkt",
                "runnable": True,
                "runnable_url": normalized,
            }
        if "/profil/spieler/" in lowered:
            return {
                "source_type": "transfermarkt_player",
                "source_name": "transfermarkt",
                "runnable": True,
                "runnable_url": normalized,
            }
        club_match = __import__("re").search(r"https?://www\.transfermarkt\.com/([^/]+)/[^/]+/verein/(\d+)", normalized, __import__("re").IGNORECASE)
        if club_match:
            slug = club_match.group(1)
            club_id = club_match.group(2)
            return {
                "source_type": "transfermarkt_club_page",
                "source_name": "transfermarkt",
                "runnable": True,
                "runnable_url": f"https://www.transfermarkt.com/{slug}/kader/verein/{club_id}",
            }
        return {"source_type": "transfermarkt_other", "source_name": "transfermarkt", "runnable": False, "runnable_url": None}
    if "fbref.com" in lowered:
        return {"source_type": "fbref_stats", "source_name": "fbref", "runnable": False, "runnable_url": None}
    if "sofascore.com" in lowered:
        team_match = re.search(r"/team/[^/]+/(\d+)", lowered)
        team_id = team_match.group(1) if team_match else "39723"
        return {
            "source_type": "sofascore_team",
            "source_name": "sofascore",
            "runnable": True,
            "runnable_url": f"https://www.sofascore.com/football/team/independiente-del-valle/{team_id}",
        }
    if "whoscored.com" in lowered:
        return {"source_type": "whoscored_page", "source_name": "whoscored", "runnable": False, "runnable_url": None}
    return {"source_type": "unknown", "source_name": "unknown", "runnable": False, "runnable_url": None}


def build_source_queue(urls: list[str]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for priority, url in enumerate(urls, start=1):
        classification = classify_source_url(url)
        queue.append(
            {
                "priority": priority,
                "url": url,
                "source_name": classification["source_name"],
                "source_type": classification["source_type"],
                "runnable": bool(classification["runnable"]),
                "runnable_url": classification.get("runnable_url"),
            }
        )
    return queue


def discover_idv_source_urls(
    query: str = "Independiente del Valle player stats transfermarkt fbref sofascore",
    *,
    max_results: int = 10,
) -> dict[str, Any]:
    """
    Discover candidate source URLs for IDV data collection using Tavily.

    This is intentionally best-effort:
    - returns a stable empty-result payload when Tavily is disabled/unconfigured
    - does not raise on network/API failures (so scrape plan remains usable)
    """

    context = {"query": query, "max_results": max_results}
    if not settings.tavily_enabled:
        return {
            "enabled": False,
            "configured": bool(settings.tavily_api_key),
            "status": "disabled",
            "query": query,
            "urls": [],
            "raw_results": [],
        }

    if not settings.tavily_api_key:
        return {
            "enabled": True,
            "configured": False,
            "status": "unconfigured",
            "query": query,
            "urls": [],
            "raw_results": [],
        }

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max(1, min(int(max_results), 20)),
    }
    try:
        log_event(logger, logging.INFO, "tavily.search.start", **context)
        response = requests.post(_TAVILY_SEARCH_URL, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
        results = body.get("results") or []
        if not isinstance(results, list):
            results = []

        filtered: list[dict[str, Any]] = []
        urls: list[str] = []
        for row in results:
            if not isinstance(row, dict):
                continue
            url = str(row.get("url") or "").strip()
            if not url:
                continue
            if not any(domain in url for domain in _ALLOWED_DOMAINS):
                continue
            filtered.append(
                {
                    "title": row.get("title"),
                    "url": url,
                    "score": row.get("score"),
                    "content_snippet": row.get("content"),
                }
            )
            urls.append(url)

        # Preserve order while de-duplicating.
        deduped_urls = list(dict.fromkeys(urls))
        source_queue = build_source_queue(deduped_urls)
        log_event(
            logger,
            logging.INFO,
            "tavily.search.complete",
            total_results=len(results),
            filtered_results=len(filtered),
            deduped_urls=len(deduped_urls),
            runnable_targets=sum(1 for row in source_queue if row["runnable"]),
            **context,
        )
        return {
            "enabled": True,
            "configured": True,
            "status": "ok",
            "query": query,
            "urls": deduped_urls,
            "source_queue": source_queue,
            "raw_results": filtered,
        }
    except requests.RequestException as exc:
        log_exception(logger, "tavily.search.failed", exc, **context)
        return {
            "enabled": True,
            "configured": True,
            "status": "request_failed",
            "query": query,
            "urls": [],
            "source_queue": [],
            "raw_results": [],
            "error": str(exc),
        }
    except ValueError as exc:
        log_exception(logger, "tavily.search.invalid_json", exc, **context)
        return {
            "enabled": True,
            "configured": True,
            "status": "invalid_json",
            "query": query,
            "urls": [],
            "source_queue": [],
            "raw_results": [],
            "error": str(exc),
        }
