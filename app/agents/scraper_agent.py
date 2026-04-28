from __future__ import annotations

import logging

from app.agents.types import AgentStepResult, AgentTask
from app.scraping.players import (
    build_idv_source_queue,
    get_idv_player_scrape_plan,
    scrape_idv_player_from_transfermarkt,
    scrape_idv_sofascore,
)
from app.scraping.tavily import discover_idv_source_urls
from app.services.logging_service import get_logger, log_event


AGENT_NAME = "scraper"
SUPPORTED_TASK_KINDS = {"scrape_players", "full_refresh"}
logger = get_logger(__name__)


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported scraper task kind: {task.kind}")

    payload = dict(task.payload)
    plan = get_idv_player_scrape_plan()
    artifacts: dict[str, object] = {"scrape_plan": plan}
    summary = f"Prepared scraping plan for {plan['scope']}."

    discovery_query = payload.get("discovery_query")
    if discovery_query:
        discovery = discover_idv_source_urls(str(discovery_query))
        artifacts["source_discovery"] = discovery
        if discovery.get("urls"):
            summary = f"Prepared scraping plan and discovered {len(discovery['urls'])} candidate source URLs."
        log_event(
            logger,
            logging.INFO,
            "scraper.discovery.complete",
            status=discovery.get("status"),
            urls_found=len(discovery.get("urls", [])),
        )
    elif bool(payload.get("use_discovered_sources")):
        discovery = build_idv_source_queue()
        artifacts["source_discovery"] = discovery
        log_event(
            logger,
            logging.INFO,
            "scraper.discovery.complete",
            status=discovery.get("status"),
            urls_found=len(discovery.get("candidate_urls", [])),
        )

    source_url = payload.get("url")
    source_queue = ((artifacts.get("source_discovery") or {}).get("source_queue") or []) if isinstance(artifacts.get("source_discovery"), dict) else []
    runnable_targets = [row for row in source_queue if isinstance(row, dict) and row.get("runnable")]
    if not source_url and runnable_targets:
        selected_target = dict(runnable_targets[0])
        source_url = selected_target.get("runnable_url") or selected_target.get("url")
        selected_target["selected_url"] = source_url
        artifacts["selected_source_target"] = selected_target

    selected_source_name = payload.get("source_name")
    if not selected_source_name and isinstance(artifacts.get("selected_source_target"), dict):
        selected_source_name = artifacts["selected_source_target"].get("source_name")

    if source_url:
        if str(selected_source_name or "").lower() == "sofascore":
            scrape_result = scrape_idv_sofascore(headless=bool(payload.get("headless", True)))
        else:
            scrape_result = scrape_idv_player_from_transfermarkt(
                str(source_url),
                headless=bool(payload.get("headless", True)),
            )
        artifacts["scrape_result"] = scrape_result
        summary = f"Scraped player data from {source_url}."

    return AgentStepResult(
        agent_name=AGENT_NAME,
        task_kind=task.kind,
        status="ok",
        summary=summary,
        artifacts=artifacts,
        metadata={"supported_task_kinds": sorted(SUPPORTED_TASK_KINDS)},
    )
