from __future__ import annotations

import logging
import re
from urllib.parse import urljoin, urlparse

import requests

from app.scraping.browser import BrowserConfig, fetch_page_html
from app.scraping.parsers import parse_player_profile, parse_transfer_history, parse_transfermarkt_squad_players
from app.scraping.sofascore import scrape_sofascore_team_stats
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify
from app.scraping.validation import validate_transfermarkt_payload
from app.config import settings
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)
_CEAPI_BASE_URL = "https://www.transfermarkt.com/ceapi/performance-game"
_TM_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "transfermarkt-player"
    return slugify(path.split("/")[-1])


def _extract_player_id(profile_url: str | None) -> str | None:
    if not profile_url:
        return None
    match = re.search(r"/spieler/(\d+)", profile_url)
    return match.group(1) if match else None


def _extract_club_id(source_url: str | None) -> str | None:
    if not source_url:
        return None
    match = re.search(r"/verein/(\d+)", source_url)
    return match.group(1) if match else None


def _as_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(str(value)))
        except (TypeError, ValueError):
            return None


def _first_int(*values: object) -> int | None:
    for value in values:
        parsed = _as_int(value)
        if parsed is not None:
            return parsed
    return None


def _enrich_squad_players_from_profile_pages(
    source_url: str,
    squad_players: list[dict[str, object]],
) -> list[dict[str, object]]:
    enriched_rows: list[dict[str, object]] = []
    for row in squad_players:
        profile_url = str(row.get("profile_url") or "").strip()
        if not profile_url:
            enriched_rows.append(row)
            continue
        absolute_profile_url = urljoin(source_url, profile_url)
        try:
            response = requests.get(
                absolute_profile_url,
                headers={**_TM_HEADERS, "Referer": source_url},
                timeout=30,
            )
            response.raise_for_status()
            profile_payload = parse_player_profile(response.text, absolute_profile_url)
        except requests.RequestException as exc:
            log_exception(
                logger,
                "scrape.transfermarkt_profile_enrichment_failed",
                exc,
                profile_url=absolute_profile_url,
            )
            enriched_rows.append(row)
            continue

        enriched_row = dict(row)
        if profile_payload.get("position"):
            enriched_row["position"] = profile_payload.get("position")
        if profile_payload.get("date_of_birth"):
            enriched_row["date_of_birth"] = profile_payload.get("date_of_birth")
        if profile_payload.get("nationality"):
            enriched_row["nationality"] = profile_payload.get("nationality")
        if profile_payload.get("market_value"):
            enriched_row["market_value"] = profile_payload.get("market_value")
        if profile_payload.get("current_club"):
            enriched_row["current_club"] = profile_payload.get("current_club")
        enriched_rows.append(enriched_row)
    return enriched_rows


def _fetch_transfermarkt_ceapi_performance(
    player_id: str,
    *,
    source_url: str,
    player_name: str,
    club_name: str | None,
    target_club_id: str | None,
) -> list[dict[str, object]]:
    endpoint = f"{_CEAPI_BASE_URL}/{player_id}"
    response = requests.get(endpoint, headers={**_TM_HEADERS, "Referer": source_url}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    performance_rows = (payload.get("data") or {}).get("performance") or []
    if not isinstance(performance_rows, list):
        return []

    mapped: list[dict[str, object]] = []
    for row in performance_rows:
        if not isinstance(row, dict):
            continue
        clubs = row.get("clubsInformation") or {}
        player_club_id = str((clubs.get("club") or {}).get("clubId") or "")
        if target_club_id and player_club_id and player_club_id != target_club_id:
            continue

        stats = row.get("statistics") or {}
        playing = stats.get("playingTimeStatistics") or {}
        goals = stats.get("goalStatistics") or {}
        cards = stats.get("cardStatistics") or {}
        distribution = stats.get("distributionStatistics") or {}
        minutes = playing.get("playedMinutes")

        if minutes is None and goals.get("goalsScoredTotal") is None and goals.get("assists") is None:
            continue

        game = row.get("gameInformation") or {}
        game_id = str(game.get("gameId") or "")
        date_blob = game.get("date") or {}
        mapped.append(
            {
                "source": "transfermarkt_ceapi",
                "source_url": f"https://www.transfermarkt.com/spielbericht/index/spielbericht/{game_id}" if game_id else source_url,
                "table_id": "transfermarkt_ceapi_performance_game",
                "player_name": player_name,
                "club_name": club_name,
                "match_date": date_blob.get("dateTimeUTC"),
                "match_external_id": game_id or None,
                "minutes": minutes or 0,
                "goals": goals.get("goalsScoredTotal") or 0,
                "assists": goals.get("assists") or 0,
                "yellow_cards": _first_int(cards.get("yellowCardGross"), cards.get("yellowCards")) or 0,
                "red_cards": _first_int(cards.get("redCardGross"), cards.get("redCards")) or 0,
                "shots": _first_int(
                    goals.get("scoringAttempts"),
                    goals.get("scoringAttemptsOnGoal"),
                )
                or 0,
                "passes_completed": _first_int(distribution.get("passesReached"), distribution.get("passes")) or 0,
                "xg": None,
                "xa": None,
                "progressive_carries": None,
                "progressive_passes": None,
                "progressive_receptions": None,
                "carries_into_final_third": None,
                "passes_into_final_third": None,
                "carries_into_penalty_area": None,
                "passes_into_penalty_area": None,
                "competition_id": game.get("competitionId"),
                "season_id": game.get("seasonId"),
            }
        )
    return mapped


def scrape_transfermarkt_player(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    runtime_slug = slug or _slug_from_url(url)
    context = {"source": "transfermarkt", "slug": runtime_slug, "url": url, "headless": headless}
    log_event(logger, logging.INFO, "scrape.start", **context)
    try:
        html = fetch_page_html(url, BrowserConfig(headless=headless), source="transfermarkt", slug=runtime_slug)
        raw_path = save_raw_html(runtime_slug, html)
        log_event(logger, logging.INFO, "scrape.raw_saved", raw_html_path=raw_path, html_length=len(html), **context)

        profile = parse_player_profile(html, url)
        transfers = parse_transfer_history(html, url)
        squad_players = parse_transfermarkt_squad_players(html, url)
        squad_players = _enrich_squad_players_from_profile_pages(url, squad_players)
        target_club_id = _extract_club_id(url)
        squad_player_match_stats: list[dict[str, object]] = []
        for squad_player in squad_players:
            player_name = str(squad_player.get("player_name") or "").strip()
            if not player_name:
                continue
            player_id = _extract_player_id(str(squad_player.get("profile_url") or ""))
            if not player_id:
                continue
            try:
                squad_player_match_stats.extend(
                    _fetch_transfermarkt_ceapi_performance(
                        player_id,
                        source_url=url,
                        player_name=player_name,
                        club_name=profile.get("current_club"),
                        target_club_id=target_club_id,
                    )
                )
            except requests.RequestException as exc:
                log_exception(
                    logger,
                    "scrape.transfermarkt_ceapi_failed",
                    exc,
                    player_name=player_name,
                    player_id=player_id,
                    endpoint=f"{_CEAPI_BASE_URL}/{player_id}",
                    **context,
                )
        sofascore_artifact: dict[str, object] | None = None
        if settings.sofascore_enabled:
            try:
                sofascore_artifact = scrape_sofascore_team_stats(headless=headless)
            except Exception as exc:
                log_exception(logger, "scrape.sofascore.enrichment_failed", exc, **context)
        diagnostics = validate_transfermarkt_payload(profile, transfers)
        payload = {
            "profile": profile,
            "transfers": transfers,
            "squad_players": squad_players,
            "squad_player_match_stats": squad_player_match_stats,
            "sofascore_artifact": sofascore_artifact,
            "diagnostics": diagnostics,
        }
        profile_fields = diagnostics["record_counts"]["profile_fields_present"]
        transfer_count = diagnostics["record_counts"]["transfer_rows"]
        log_event(
            logger,
            logging.INFO,
            "scrape.records_extracted",
            profile_fields=profile_fields,
            transfer_count=transfer_count,
            squad_player_count=len(squad_players),
            squad_player_match_stats_count=len(squad_player_match_stats),
            extraction_status=diagnostics["extraction_status"],
            missing_required_fields=diagnostics["missing_required_fields"],
            **context,
        )
        if diagnostics["extraction_status"] != "success_complete":
            log_event(
                logger,
                logging.WARNING,
                "scrape.empty_result",
                profile_fields=profile_fields,
                transfer_count=transfer_count,
                extraction_status=diagnostics["extraction_status"],
                missing_required_fields=diagnostics["missing_required_fields"],
                **context,
            )

        parsed_path = save_parsed_payload(runtime_slug, payload)
        log_event(logger, logging.INFO, "scrape.parsed_saved", parsed_data_path=parsed_path, **context)
        log_event(logger, logging.INFO, "scrape.success", parsed_data_path=parsed_path, raw_html_path=raw_path, extraction_status=diagnostics["extraction_status"], **context)

        return {
            "slug": runtime_slug,
            "raw_html_path": raw_path,
            "parsed_data_path": parsed_path,
            "payload": payload,
        }
    except Exception as exc:
        log_exception(logger, "scrape.failed", exc, stage="transfermarkt_pipeline", **context)
        raise
