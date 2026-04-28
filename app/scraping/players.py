from app.scraping.transfermarkt import scrape_transfermarkt_player
from app.scraping.sofascore import scrape_sofascore_team_stats
from app.scraping.tavily import discover_idv_source_urls


def build_idv_source_queue(query: str | None = None) -> dict[str, object]:
    discovery = discover_idv_source_urls(query or "Independiente del Valle player stats transfermarkt fbref sofascore")
    return {
        "provider": "tavily",
        "status": discovery.get("status"),
        "configured": discovery.get("configured"),
        "candidate_urls": discovery.get("urls", [])[:10],
        "source_queue": discovery.get("source_queue", []),
    }


def get_idv_player_scrape_plan() -> dict[str, object]:
    """Return the current scraping plan for the MVP."""

    discovery = build_idv_source_queue()
    return {
        "scope": "IDV players",
        "source": "transfermarkt",
        "source_discovery": discovery,
        "targets": [
            "player profiles",
            "transfer history",
            "match performance (transfermarkt ceapi)",
            "match enrichment (sofascore lineups)",
            "raw html",
            "parsed json payloads",
        ],
        "rate_limit_strategy": "serialized Playwright fetches with delay between requests",
        "status": "playwright-backed scraper scaffolded",
    }


def scrape_idv_player_from_transfermarkt(url: str, *, headless: bool = True) -> dict[str, object]:
    """High-level entrypoint for scraping an IDV player page from Transfermarkt."""

    return scrape_transfermarkt_player(url, headless=headless)


def scrape_idv_sofascore(*, headless: bool = True) -> dict[str, object]:
    """High-level entrypoint for scraping recent IDV team stats from Sofascore."""

    return scrape_sofascore_team_stats(headless=headless)
