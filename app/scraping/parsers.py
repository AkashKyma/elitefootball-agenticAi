from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
import logging
import re
from urllib.parse import urlparse

from app.services.logging_service import get_logger, is_debug_enabled, log_event


logger = get_logger(__name__)
TRANSFERMARKT_LABELS = (
    "Name in home country",
    "Position",
    "Date of birth",
    "Citizenship",
    "Current club",
    "Market value",
)


class _TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_data(self) -> str:
        return " ".join(part.strip() for part in self.parts if part.strip())


def strip_tags(value: str) -> str:
    parser = _TagStripper()
    parser.feed(value)
    return normalize_space(unescape(parser.get_data()))


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_meta_content(html: str, attr_name: str, attr_value: str) -> str | None:
    pattern = rf'<meta[^>]+{attr_name}=["\']{re.escape(attr_value)}["\'][^>]+content=["\']([^"\']+)["\']'
    match = re.search(pattern, html, re.IGNORECASE)
    return normalize_space(unescape(match.group(1))) if match else None


def extract_title(html: str) -> str | None:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return normalize_space(strip_tags(match.group(1))) if match else None


def extract_itemprop_content(html: str, itemprop: str) -> str | None:
    pattern = rf'itemprop=["\']{re.escape(itemprop)}["\'][^>]*>(.*?)</'
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = normalize_space(strip_tags(match.group(1)))
    return value or None


def extract_json_ld(html: str) -> dict[str, object]:
    match = re.search(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {}

    raw_payload = match.group(1).strip()
    try:
        return json.loads(raw_payload)
    except json.JSONDecodeError:
        return {}


def _label_stop_pattern(label: str) -> str:
    other_labels = [candidate for candidate in TRANSFERMARKT_LABELS if candidate.lower() != label.lower()]
    escaped = "|".join(re.escape(item) for item in other_labels)
    return rf"(?:{escaped})"


def extract_labeled_value(html: str, label: str) -> str | None:
    inline_pattern = rf">\s*{re.escape(label)}\s*:?\s*(.*?)</(?:div|span|p|td|li|a|strong|b)>"
    inline_match = re.search(inline_pattern, html, re.IGNORECASE | re.DOTALL)
    if inline_match:
        value = normalize_space(strip_tags(inline_match.group(1)))
        return value or None

    pattern = rf"{re.escape(label)}\s*</[^>]+>\s*<[^>]+>(.*?)</"
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if match:
        value = normalize_space(strip_tags(match.group(1)))
        return value or None

    stripped_html = strip_tags(html)
    text_pattern = rf"{re.escape(label)}\s*:?\s*(.+?)(?=\s+(?:{_label_stop_pattern(label)})\s*:|$)"
    text_match = re.search(text_pattern, stripped_html, re.IGNORECASE)
    if text_match:
        value = normalize_space(text_match.group(1))
        return value or None
    return None


def _clean_player_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = normalize_space(value)
    cleaned = re.sub(r"\s+-\s+.*$", "", cleaned).strip()
    cleaned = re.sub(r"\s+\|\s+.*$", "", cleaned).strip()
    return cleaned or None


def is_transfermarkt_squad_page_url(source_url: str) -> bool:
    """Kader/squad list pages are not single-player profiles; do not treat title as a player name."""
    try:
        return "/kader/" in urlparse(source_url).path.lower()
    except Exception:
        return False


def club_name_from_transfermarkt_club_url(source_url: str) -> str | None:
    """Best-effort club label from a TM path like /independiente-del-valle/kader/..."""
    try:
        parts = [p for p in urlparse(source_url).path.strip("/").split("/") if p]
    except Exception:
        return None
    if not parts:
        return None
    slug = parts[0]
    if slug in {"kader", "spielplan", "www", "com"}:
        return None
    if slug.isdigit():
        return None
    display = normalize_space(slug.replace("-", " "))
    return display.title() if display else None


def _looks_like_transfermarkt_market_value(value: str) -> bool:
    """Ignore loose 'k'/'m' matches that catch player names (e.g. *Mate*o*)."""
    v = value.strip()
    if not v:
        return False
    if "€" in v or "$" in v:
        return True
    return bool(re.search(r"^\d+([.,]\d+)?\s*([KMBkmb]|[Kk](\s|\.|$)?|[mM](\s|\.|$|io)?)", v))


def _sanitize_market_value(value: str | None) -> str | None:
    cleaned = normalize_space(value or "")
    if not cleaned:
        return None
    return cleaned if _looks_like_transfermarkt_market_value(cleaned) else None


def _extract_market_value_from_header(html: str) -> str | None:
    match = re.search(
        r'class=["\']data-header__market-value-wrapper["\'][^>]*>(.*?)<p class=["\']data-header__last-update["\']',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    value = normalize_space(strip_tags(match.group(1)))
    return _sanitize_market_value(value)


def _sanitize_date_of_birth(value: str | None) -> str | None:
    cleaned = normalize_space(value or "")
    if not cleaned:
        return None
    cleaned = re.sub(r"^\s*/?Age:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\(.*?\)\s*$", "", cleaned).strip()
    date_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b", cleaned)
    if date_match:
        return date_match.group(0)
    return cleaned or None


def _sanitize_nationality(value: str | None) -> str | None:
    cleaned = normalize_space(value or "")
    if not cleaned:
        return None
    cleaned = cleaned.replace("�", "").strip()
    cleaned = re.sub(r"[^\w\s\-/,]+$", "", cleaned).strip()
    return cleaned or None


def parse_player_profile(html: str, source_url: str) -> dict[str, object]:
    if is_transfermarkt_squad_page_url(source_url):
        log_event(
            logger,
            logging.INFO,
            "parse.profile.squad_list_skip",
            source="transfermarkt",
            source_url=source_url,
        )
        return {
            "source": "transfermarkt",
            "source_url": source_url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "player_name": None,
            "preferred_name": None,
            "position": None,
            "date_of_birth": None,
            "nationality": None,
            "current_club": club_name_from_transfermarkt_club_url(source_url),
            "market_value": None,
        }
    log_event(logger, logging.INFO, "parse.profile.start", source="transfermarkt", source_url=source_url)
    json_ld = extract_json_ld(html)
    player_name = (
        json_ld.get("name")
        if isinstance(json_ld, dict)
        else None
    ) or extract_meta_content(html, "property", "og:title") or extract_title(html)

    profile = {
        "source": "transfermarkt",
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "player_name": _clean_player_name(player_name),
        "preferred_name": extract_labeled_value(html, "Name in home country"),
        "position": extract_labeled_value(html, "Position"),
        "date_of_birth": _sanitize_date_of_birth(
            extract_labeled_value(html, "Date of birth")
            or extract_labeled_value(html, "Date of birth/Age")
            or extract_itemprop_content(html, "birthDate")
        ),
        "nationality": _sanitize_nationality(
            extract_labeled_value(html, "Citizenship") or extract_itemprop_content(html, "nationality")
        ),
        "current_club": extract_labeled_value(html, "Current club"),
        "market_value": _sanitize_market_value(extract_labeled_value(html, "Market value")) or _extract_market_value_from_header(html),
    }
    present_fields = sum(1 for key, value in profile.items() if key not in {"source", "source_url", "scraped_at"} and value)
    log_event(
        logger,
        logging.INFO,
        "parse.profile.complete",
        source="transfermarkt",
        source_url=source_url,
        fields_found=present_fields,
        expected_fields=6,
        used_json_ld=bool(isinstance(json_ld, dict) and json_ld),
    )
    if present_fields <= 1:
        log_event(logger, logging.WARNING, "parse.partial_result", source="transfermarkt", source_url=source_url, fields_found=present_fields)
    elif is_debug_enabled() and not json_ld:
        log_event(logger, logging.DEBUG, "parse.profile.fallback_used", source="transfermarkt", source_url=source_url, fallback="meta_or_title")
    return profile


def _looks_like_transfer_row(cleaned: list[str]) -> bool:
    if len(cleaned) < 4:
        return False
    lowered = [value.lower() for value in cleaned]
    joined = " ".join(lowered)
    if "season" in joined and "joined" in joined:
        return False
    season = cleaned[0]
    if not re.search(r"\d{2}/\d{2}|\d{4}/\d{2}|\d{4}", season):
        return False
    return any(value and value not in {"-", "?"} for value in cleaned[2:4])


def parse_transfer_history(html: str, source_url: str) -> list[dict[str, object]]:
    log_event(logger, logging.INFO, "parse.transfers.start", source="transfermarkt", source_url=source_url)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    transfers: list[dict[str, object]] = []

    for row in rows:
        columns = [strip_tags(column) for column in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.IGNORECASE | re.DOTALL)]
        cleaned = [column for column in columns if column]
        if not _looks_like_transfer_row(cleaned):
            continue

        transfers.append(
            {
                "season": cleaned[0] if len(cleaned) > 0 else None,
                "date": cleaned[1] if len(cleaned) > 1 else None,
                "from_club": cleaned[2] if len(cleaned) > 2 else None,
                "to_club": cleaned[3] if len(cleaned) > 3 else None,
                "market_value": cleaned[4] if len(cleaned) > 4 else None,
                "fee": cleaned[5] if len(cleaned) > 5 else None,
                "source_url": source_url,
            }
        )

    log_event(logger, logging.INFO, "parse.transfers.complete", source="transfermarkt", source_url=source_url, row_candidates=len(rows), records_extracted=len(transfers))
    if not transfers:
        log_event(logger, logging.WARNING, "parse.partial_result", source="transfermarkt", source_url=source_url, records_extracted=0, section="transfers")
    return transfers


def parse_transfermarkt_squad_players(html: str, source_url: str) -> list[dict[str, object]]:
    """Parse player rows from a Transfermarkt squad page when present."""

    log_event(logger, logging.INFO, "parse.squad.start", source="transfermarkt", source_url=source_url)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    parsed_rows: list[dict[str, object]] = []
    seen_names: set[str] = set()

    for row in rows:
        if "/profil/spieler/" not in row:
            continue

        link_match = re.search(r'href=["\']([^"\']*/profil/spieler/[^"\']+)["\']', row, re.IGNORECASE)
        name_match = re.search(
            r'<a[^>]*href=["\'][^"\']*/profil/spieler/[^"\']+["\'][^>]*>(.*?)</a>',
            row,
            re.IGNORECASE | re.DOTALL,
        )
        if not name_match:
            continue

        player_name = normalize_space(strip_tags(name_match.group(1)))
        if not player_name:
            continue
        dedupe_key = player_name.lower()
        if dedupe_key in seen_names:
            continue
        seen_names.add(dedupe_key)

        columns = [strip_tags(column) for column in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.IGNORECASE | re.DOTALL)]
        cleaned = [normalize_space(value) for value in columns if normalize_space(value)]

        position = None
        age = None
        market_value = None
        for value in cleaned:
            lower_value = value.lower()
            if position is None and any(
                token in lower_value
                for token in ("goalkeeper", "defender", "midfielder", "forward", "attack", "winger", "striker")
            ):
                position = value
            if age is None and re.fullmatch(r"\d{2}", value):
                age = value
            if market_value is None and _looks_like_transfermarkt_market_value(
                value
            ) and normalize_space(value).casefold() != player_name.casefold():
                market_value = value

        parsed_rows.append(
            {
                "source": "transfermarkt",
                "source_url": source_url,
                "player_name": player_name,
                "profile_url": link_match.group(1) if link_match else None,
                "position": position,
                "age": age,
                "market_value": market_value,
            }
        )

    log_event(
        logger,
        logging.INFO,
        "parse.squad.complete",
        source="transfermarkt",
        source_url=source_url,
        row_candidates=len(rows),
        records_extracted=len(parsed_rows),
    )
    if not parsed_rows:
        log_event(logger, logging.WARNING, "parse.partial_result", source="transfermarkt", source_url=source_url, records_extracted=0, section="squad_players")
    return parsed_rows
