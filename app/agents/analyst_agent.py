from __future__ import annotations

from app.agents.types import AgentStepResult, AgentTask
from app.analysis.advanced_metrics_engine import build_advanced_metrics_output
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.similarity_engine import build_similarity_output
from app.analysis.valuation_engine import build_valuation_output
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables


AGENT_NAME = "analyst"
SUPPORTED_TASK_KINDS = {"run_analysis", "full_refresh"}


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported analyst task kind: {task.kind}")

    silver_tables = task.metadata.get("silver_tables")
    gold_tables = task.metadata.get("gold_tables")
    if silver_tables is None:
        silver_tables = build_silver_tables()["tables"]
    if gold_tables is None:
        gold_tables = build_gold_features(silver_tables)["tables"]

    kpi = build_kpi_engine_output(silver_tables)
    advanced_metrics = build_advanced_metrics_output(silver_tables)
    similarity = build_similarity_output(silver_tables, gold_tables, kpi["rows"])
    valuation = build_valuation_output(silver_tables, gold_tables, kpi["rows"], advanced_metrics["rows"])

    return AgentStepResult(
        agent_name=AGENT_NAME,
        task_kind=task.kind,
        status="ok",
        summary="Built KPI, advanced metrics, similarity, and valuation outputs.",
        artifacts={
            "kpi": kpi,
            "advanced_metrics": advanced_metrics,
            "similarity": similarity,
            "valuation": valuation,
        },
        metadata={
            "supported_task_kinds": sorted(SUPPORTED_TASK_KINDS),
            "silver_tables": silver_tables,
            "gold_tables": gold_tables,
        },
    )
