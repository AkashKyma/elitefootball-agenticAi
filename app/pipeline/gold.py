from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


def _minutes_bucket(minutes: int | None) -> str:
    if minutes is None:
        return "unknown"
    if minutes < 30:
        return "bench"
    if minutes < 75:
        return "rotation"
    return "starter"


def build_gold_features(silver_tables: dict[str, list[dict[str, Any]]]) -> dict[str, object]:
    player_totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "player_name": None,
            "matches": 0,
            "minutes": 0,
            "goals": 0,
            "assists": 0,
            "shots": 0,
            "yellow_cards": 0,
            "red_cards": 0,
        }
    )

    for row in silver_tables.get("player_match_stats", []):
        player_name = row.get("player_name") or "unknown-player"
        total = player_totals[player_name]
        total["player_name"] = player_name
        total["matches"] += 1
        total["minutes"] += row.get("minutes") or 0
        total["goals"] += row.get("goals") or 0
        total["assists"] += row.get("assists") or 0
        total["shots"] += row.get("shots") or 0
        total["yellow_cards"] += row.get("yellow_cards") or 0
        total["red_cards"] += row.get("red_cards") or 0

    player_features = []
    for total in player_totals.values():
        minutes = total["minutes"]
        goal_contributions = total["goals"] + total["assists"]
        feature_row = {
            **total,
            "goal_contributions": goal_contributions,
            "goal_contribution_per_90": round((goal_contributions / minutes) * 90, 3) if minutes else None,
            "shot_involvement_flag": total["shots"] > 0,
            "discipline_risk_score": total["yellow_cards"] + (total["red_cards"] * 2),
            "minutes_bucket": _minutes_bucket(minutes),
        }
        player_features.append(feature_row)

    match_features = []
    for row in silver_tables.get("matches", []):
        home_score = row.get("home_score")
        away_score = row.get("away_score")
        match_features.append(
            {
                "source_url": row.get("source_url"),
                "external_id": row.get("external_id"),
                "home_club": row.get("home_club"),
                "away_club": row.get("away_club"),
                "score_difference": (home_score - away_score) if home_score is not None and away_score is not None else None,
                "is_draw": home_score == away_score if home_score is not None and away_score is not None else None,
                "total_goals": (home_score + away_score) if home_score is not None and away_score is not None else None,
                "idv_involved_flag": "idv" in ((row.get("home_club") or "") + (row.get("away_club") or "")).lower(),
            }
        )

    paths = {
        "player_features": write_json(Path(settings.gold_data_dir) / "player_features.json", player_features),
        "match_features": write_json(Path(settings.gold_data_dir) / "match_features.json", match_features),
    }
    return {"paths": paths, "tables": {"player_features": player_features, "match_features": match_features}}
