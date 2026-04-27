from dataclasses import dataclass
import os


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
    raw_data_dir: str = os.getenv("RAW_DATA_DIR", "data/raw/transfermarkt")
    parsed_data_dir: str = os.getenv("PARSED_DATA_DIR", "data/parsed/transfermarkt")
    fbref_raw_data_dir: str = os.getenv("FBREF_RAW_DATA_DIR", "data/raw/fbref")
    fbref_parsed_data_dir: str = os.getenv("FBREF_PARSED_DATA_DIR", "data/parsed/fbref")
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
