from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.scraping.storage import save_parsed_payload
from app.services.logging_service import get_logger, log_event, log_exception

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


logger = get_logger(__name__)


def _first_number(*values: object) -> float | None:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _map_player_stat_row(
    *,
    team_id: int,
    event_id: int,
    event: dict[str, Any],
    player_row: dict[str, Any],
) -> dict[str, Any] | None:
    player = player_row.get("player") or {}
    name = player.get("name")
    if not name:
        return None
    stats = player_row.get("statistics") or {}
    if not isinstance(stats, dict):
        return None

    minutes = _first_number(stats.get("minutesPlayed"))
    goals = _first_number(stats.get("goals"), stats.get("goalScored"), stats.get("goalsScored")) or 0
    assists = _first_number(stats.get("goalAssist"), stats.get("assists")) or 0
    shots = _first_number(stats.get("totalShots"), stats.get("shotsTotal"), stats.get("shots")) or 0
    passes_completed = _first_number(stats.get("accuratePass"), stats.get("successfulPasses"))
    yellow_cards = _first_number(stats.get("yellowCards"), stats.get("yellowCard")) or 0
    red_cards = _first_number(stats.get("redCards"), stats.get("redCard")) or 0

    # Advanced metrics: use direct values when present.
    xg = _first_number(stats.get("expectedGoals"), stats.get("xg"))
    xa = _first_number(stats.get("expectedAssists"), stats.get("xa"))

    # Progressive-like proxies from available Sofa fields.
    progressive_passes = _first_number(
        stats.get("accurateFinalThirdPasses"),
        stats.get("totalFinalThirdPasses"),
        stats.get("accurateOwnHalfPasses"),
    )
    progressive_carries = _first_number(
        stats.get("dribblesSucceeded"),
        stats.get("successfulDribbles"),
    )
    progressive_receptions = _first_number(stats.get("touches"))

    match_date = ((event.get("startTimestamp") or 0) and int(event.get("startTimestamp")))
    match_date_iso = None
    if match_date:
        from datetime import UTC, datetime

        match_date_iso = datetime.fromtimestamp(match_date, tz=UTC).isoformat().replace("+00:00", "Z")

    return {
        "source": "sofascore",
        "source_url": f"https://www.sofascore.com/event/{event_id}",
        "table_id": "sofascore_lineups",
        "player_name": str(name).strip(),
        "club_name": (event.get("homeTeam") or {}).get("name")
        if int((event.get("homeTeam") or {}).get("id") or -1) == team_id
        else (event.get("awayTeam") or {}).get("name"),
        "match_date": match_date_iso,
        "match_external_id": str(event_id),
        "minutes": int(minutes or 0),
        "goals": int(goals),
        "assists": int(assists),
        "yellow_cards": int(yellow_cards),
        "red_cards": int(red_cards),
        "shots": int(shots),
        "passes_completed": int(passes_completed or 0),
        "xg": xg,
        "xa": xa,
        "progressive_carries": int(progressive_carries) if progressive_carries is not None else None,
        "progressive_passes": int(progressive_passes) if progressive_passes is not None else None,
        "progressive_receptions": int(progressive_receptions) if progressive_receptions is not None else None,
    }


def scrape_sofascore_team_stats(
    team_id: int = settings.sofascore_team_id,
    *,
    recent_events_limit: int = settings.sofascore_recent_events_limit,
    headless: bool = True,
) -> dict[str, object]:
    context = {"source": "sofascore", "team_id": team_id, "headless": headless, "recent_events_limit": recent_events_limit}
    log_event(logger, logging.INFO, "scrape.sofascore.start", **context)
    if sync_playwright is None:
        payload = {
            "team_id": team_id,
            "status": "playwright_unavailable",
            "player_match_stats": [],
            "events_processed": 0,
        }
        parsed_path = save_parsed_payload(f"team-{team_id}", payload, directory=settings.sofascore_parsed_data_dir)
        log_event(logger, logging.WARNING, "scrape.sofascore.playwright_unavailable", parsed_data_path=parsed_path, **context)
        return {"parsed_data_path": parsed_path, "payload": payload}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            try:
                ctx = browser.new_context()
                page = ctx.new_page()
                page.goto(f"https://www.sofascore.com/football/team/independiente-del-valle/{team_id}", wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                events_resp = page.request.get(f"https://www.sofascore.com/api/v1/team/{team_id}/events/last/0")
                if events_resp.status != 200:
                    payload = {
                        "team_id": team_id,
                        "status": f"events_request_failed_{events_resp.status}",
                        "player_match_stats": [],
                        "events_processed": 0,
                    }
                    parsed_path = save_parsed_payload(f"team-{team_id}", payload, directory=settings.sofascore_parsed_data_dir)
                    log_event(logger, logging.WARNING, "scrape.sofascore.events_failed", status=events_resp.status, parsed_data_path=parsed_path, **context)
                    return {"parsed_data_path": parsed_path, "payload": payload}

                events_payload = events_resp.json()
                events = list((events_payload or {}).get("events") or [])[: max(1, recent_events_limit)]

                mapped_rows: list[dict[str, Any]] = []
                processed = 0
                for event in events:
                    event_id = int(event.get("id") or 0)
                    if not event_id:
                        continue
                    lineups_resp = page.request.get(f"https://www.sofascore.com/api/v1/event/{event_id}/lineups")
                    if lineups_resp.status != 200:
                        continue
                    lineups = lineups_resp.json()
                    for side_key in ("home", "away"):
                        side = lineups.get(side_key) or {}
                        for player_row in side.get("players") or []:
                            if int(player_row.get("teamId") or -1) != team_id:
                                continue
                            mapped = _map_player_stat_row(team_id=team_id, event_id=event_id, event=event, player_row=player_row)
                            if mapped:
                                mapped_rows.append(mapped)
                    processed += 1

                payload = {
                    "team_id": team_id,
                    "status": "ok",
                    "events_seen": len(events),
                    "events_processed": processed,
                    "player_match_stats": mapped_rows,
                }
                parsed_path = save_parsed_payload(f"team-{team_id}", payload, directory=settings.sofascore_parsed_data_dir)
                log_event(
                    logger,
                    logging.INFO,
                    "scrape.sofascore.success",
                    events_seen=len(events),
                    events_processed=processed,
                    player_match_stats_count=len(mapped_rows),
                    parsed_data_path=parsed_path,
                    **context,
                )
                return {"parsed_data_path": parsed_path, "payload": payload}
            finally:
                browser.close()
    except Exception as exc:
        log_exception(logger, "scrape.sofascore.failed", exc, **context)
        payload = {"team_id": team_id, "status": "failed", "error": str(exc), "player_match_stats": [], "events_processed": 0}
        parsed_path = save_parsed_payload(f"team-{team_id}", payload, directory=settings.sofascore_parsed_data_dir)
        return {"parsed_data_path": parsed_path, "payload": payload}
