"""
League normalization and cross-league comparison support.
Provides coefficients for adjusting player performance across competition tiers.
"""
from __future__ import annotations

LEAGUE_COEFFICIENTS: dict[str, float] = {
    # Elite (tier 1)
    "premier league": 15.0,
    "english premier league": 15.0,
    "la liga": 14.0,
    "bundesliga": 13.0,
    "serie a": 13.0,
    "ligue 1": 12.0,
    # Tier 2 European
    "eredivisie": 10.0,
    "primeira liga": 10.0,
    "portuguese liga": 10.0,
    "super lig": 9.0,
    "championship": 8.0,
    "scottish premiership": 7.0,
    "belgian pro league": 8.0,
    "austrian bundesliga": 8.0,
    "red bull liga": 8.0,
    # South American
    "copa libertadores": 8.0,
    "copa sudamericana": 6.0,
    "brasileirao": 7.0,
    "serie a (brazil)": 7.0,
    "liga mx": 6.0,
    "argentinian primera": 6.0,
    "liga pro": 5.0,
    "liga pro ecuador": 5.0,
    "ecuador liga pro": 5.0,
    # Other/unknown
    "unknown": 0.0,
    "": 0.0,
}

CLUB_TO_LEAGUE_HINTS: dict[str, str] = {
    "idv": "liga pro",
    "independiente del valle": "liga pro",
    "barcelona sc": "liga pro",
    "benfica": "primeira liga",
    "sl benfica": "primeira liga",
    "ajax": "eredivisie",
    "salzburg": "austrian bundesliga",
    "rb salzburg": "austrian bundesliga",
    "red bull salzburg": "austrian bundesliga",
    "manchester city": "premier league",
    "liverpool": "premier league",
    "real madrid": "la liga",
    "barcelona": "la liga",
    "fc barcelona": "la liga",
    "psg": "ligue 1",
    "paris saint-germain": "ligue 1",
    "porto": "primeira liga",
    "sporting cp": "primeira liga",
}


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def league_coefficient(competition: str | None, club_name: str | None = None) -> float:
    """Return league coefficient (−10 to +15 scale, where 0 = unknown baseline)."""
    comp_key = _normalize(competition)
    if comp_key and comp_key in LEAGUE_COEFFICIENTS:
        return LEAGUE_COEFFICIENTS[comp_key]

    # Partial match
    for key, coef in LEAGUE_COEFFICIENTS.items():
        if key and key in comp_key:
            return coef

    # Club hint fallback
    club_key = _normalize(club_name)
    if club_key in CLUB_TO_LEAGUE_HINTS:
        league_hint = CLUB_TO_LEAGUE_HINTS[club_key]
        return LEAGUE_COEFFICIENTS.get(league_hint, 0.0)
    for club_alias, league_hint in CLUB_TO_LEAGUE_HINTS.items():
        if club_alias and club_alias in club_key:
            return LEAGUE_COEFFICIENTS.get(league_hint, 0.0)

    return 0.0


def normalize_stat_for_league(
    stat_value: float,
    competition: str | None,
    club_name: str | None = None,
    baseline_coefficient: float = 5.0,
) -> float:
    """Scale a stat to a common baseline league level."""
    coef = league_coefficient(competition, club_name)
    if coef <= 0:
        return stat_value
    scale = baseline_coefficient / max(coef, 1.0)
    return round(stat_value * scale, 3)


def cross_league_comparison(
    players: list[dict],
    stat_key: str = "base_kpi_score",
) -> list[dict]:
    """Add league-normalized stat to a list of player rows."""
    result = []
    for row in players:
        norm = normalize_stat_for_league(
            float(row.get(stat_key) or 0.0),
            row.get("competition"),
            row.get("current_club"),
        )
        result.append({**row, f"{stat_key}_league_normalized": round(norm, 3)})
    return result


def league_tier(competition: str | None, club_name: str | None = None) -> str:
    coef = league_coefficient(competition, club_name)
    if coef >= 12:
        return "elite"
    if coef >= 8:
        return "high"
    if coef >= 5:
        return "mid"
    if coef > 0:
        return "developing"
    return "unknown"
