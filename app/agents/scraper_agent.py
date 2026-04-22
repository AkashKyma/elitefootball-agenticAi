from __future__ import annotations

from app.agents.types import AgentStepResult, AgentTask
from app.scraping.players import get_idv_player_scrape_plan, scrape_idv_player_from_transfermarkt


AGENT_NAME = "scraper"
SUPPORTED_TASK_KINDS = {"scrape_players", "full_refresh"}


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported scraper task kind: {task.kind}")

    payload = dict(task.payload)
    plan = get_idv_player_scrape_plan()
    artifacts: dict[str, object] = {"scrape_plan": plan}
    summary = f"Prepared scraping plan for {plan['scope']}."

    source_url = payload.get("url")
    if source_url:
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
