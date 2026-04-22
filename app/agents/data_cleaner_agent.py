from __future__ import annotations

from app.agents.types import AgentStepResult, AgentTask
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables


AGENT_NAME = "data_cleaner"
SUPPORTED_TASK_KINDS = {"clean_data", "full_refresh"}


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported data cleaner task kind: {task.kind}")

    bronze = build_bronze_manifest()
    silver = build_silver_tables()
    gold = build_gold_features(silver["tables"])

    return AgentStepResult(
        agent_name=AGENT_NAME,
        task_kind=task.kind,
        status="ok",
        summary="Built Bronze, Silver, and Gold cleaning artifacts.",
        artifacts={
            "bronze": bronze,
            "silver": silver,
            "gold": gold,
        },
        metadata={
            "supported_task_kinds": sorted(SUPPORTED_TASK_KINDS),
            "player_count": len(silver["tables"].get("players", [])),
            "match_stat_count": len(silver["tables"].get("player_match_stats", [])),
        },
    )
