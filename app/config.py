from dataclasses import dataclass
from pathlib import Path
import os


def _load_env_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_key = key.strip()
        env_value = value.strip()
        if not env_key:
            continue
        if (env_value.startswith('"') and env_value.endswith('"')) or (
            env_value.startswith("'") and env_value.endswith("'")
        ):
            env_value = env_value[1:-1]
        os.environ.setdefault(env_key, env_value)


def _bootstrap_env() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for env_name in (".env", ".env.local"):
        _load_env_file(repo_root / env_name)


_bootstrap_env()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the bootstrap application."""

    app_name: str = "elitefootball-agenticAi"
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./elitefootball.db")
    idv_team_key: str = os.getenv("IDV_TEAM_KEY", "idv")
    scrape_delay_seconds: float = float(os.getenv("SCRAPE_DELAY_SECONDS", "2.0"))
    scrape_timeout_ms: int = int(os.getenv("SCRAPE_TIMEOUT_MS", "30000"))
    scrape_headless: bool = _env_bool("SCRAPE_HEADLESS", True)
    scrape_use_stealth: bool = _env_bool("SCRAPE_USE_STEALTH", True)
    scrape_challenge_max_wait_ms: int = int(os.getenv("SCRAPE_CHALLENGE_MAX_WAIT_MS", "90000"))
    scrape_chromium_channel: str | None = (os.getenv("SCRAPE_CHROMIUM_CHANNEL") or "").strip() or None
    # Realistic Chrome on Windows; override if needed (e.g. match your local Chrome / Playwright build).
    scrape_user_agent: str = os.getenv(
        "SCRAPE_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36",
    )
    scrape_viewport_width: int = int(os.getenv("SCRAPE_VIEWPORT_WIDTH", "1920"))
    scrape_viewport_height: int = int(os.getenv("SCRAPE_VIEWPORT_HEIGHT", "1080"))
    scrape_locale: str = os.getenv("SCRAPE_LOCALE", "en-US")
    scrape_timezone_id: str = os.getenv("SCRAPE_TIMEZONE_ID", "America/New_York")
    scrape_user_data_dir: str | None = (os.getenv("SCRAPE_USER_DATA_DIR") or "").strip() or None
    scrape_hold_browser_open: bool = _env_bool("SCRAPE_HOLD_BROWSER_OPEN", False)
    tavily_api_key: str | None = (os.getenv("TAVILY_API_KEY") or "").strip() or None
    tavily_enabled: bool = _env_bool("TAVILY_ENABLED", True)
    sofascore_enabled: bool = _env_bool("SOFASCORE_ENABLED", True)
    sofascore_team_id: int = int(os.getenv("SOFASCORE_TEAM_ID", "39723"))
    sofascore_recent_events_limit: int = int(os.getenv("SOFASCORE_RECENT_EVENTS_LIMIT", "25"))
    raw_data_dir: str = os.getenv("RAW_DATA_DIR", "data/raw/transfermarkt")
    parsed_data_dir: str = os.getenv("PARSED_DATA_DIR", "data/parsed/transfermarkt")
    fbref_raw_data_dir: str = os.getenv("FBREF_RAW_DATA_DIR", "data/raw/fbref")
    fbref_parsed_data_dir: str = os.getenv("FBREF_PARSED_DATA_DIR", "data/parsed/fbref")
    sofascore_parsed_data_dir: str = os.getenv("SOFASCORE_PARSED_DATA_DIR", "data/parsed/sofascore")
    bronze_data_dir: str = os.getenv("BRONZE_DATA_DIR", "data/bronze")
    silver_data_dir: str = os.getenv("SILVER_DATA_DIR", "data/silver")
    gold_data_dir: str = os.getenv("GOLD_DATA_DIR", "data/gold")
    repo_root: str = os.getenv("REPO_ROOT", os.getcwd())
    safety_approval_ttl_seconds: int = int(os.getenv("SAFETY_APPROVAL_TTL_SECONDS", "900"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_debug_enabled: bool = _env_bool("LOG_DEBUG_ENABLED", False)
    log_file_enabled: bool = _env_bool("LOG_FILE_ENABLED", False)
    log_file_path: str | None = os.getenv("LOG_FILE_PATH")


settings = Settings()
