from __future__ import annotations

from app.agents.types import AgentStepResult, AgentTask


AGENT_NAME = "report_generator"
SUPPORTED_TASK_KINDS = {"generate_report", "full_refresh"}


def _artifact_row_count(payload: object) -> int | None:
    if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        return len(payload["rows"])
    return None


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported report-generator task kind: {task.kind}")

    silver_tables = task.metadata.get("silver_tables") or {}
    analysis_outputs = task.metadata.get("analysis_outputs") or {}

    player_count = len(silver_tables.get("players", [])) if isinstance(silver_tables, dict) else 0
    match_stat_count = len(silver_tables.get("player_match_stats", [])) if isinstance(silver_tables, dict) else 0
    analysis_counts = {
        name: count
        for name, count in (
            (name, _artifact_row_count(output))
            for name, output in sorted(analysis_outputs.items())
        )
        if count is not None
    }

    summary = f"Generated report for {player_count} players with {match_stat_count} match-stat rows."
    if analysis_counts:
        formatted_counts = ", ".join(f"{name}={count}" for name, count in analysis_counts.items())
        summary = f"{summary} Analysis artifacts: {formatted_counts}."

    return AgentStepResult(
        agent_name=AGENT_NAME,
        task_kind=task.kind,
        status="ok",
        summary=summary,
        artifacts={
            "report": {
                "player_count": player_count,
                "match_stat_count": match_stat_count,
                "analysis_artifact_counts": analysis_counts,
            }
        },
        metadata={"supported_task_kinds": sorted(SUPPORTED_TASK_KINDS)},
    )
