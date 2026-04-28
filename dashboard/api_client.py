from __future__ import annotations

import os
from typing import Any

import requests


DEFAULT_API_BASE_URL = "http://127.0.0.1:9001"
FALLBACK_API_BASE_URLS = ("http://127.0.0.1:9000", "http://localhost:8000")
DEFAULT_TIMEOUT_SECONDS = 10


class DashboardAPIError(RuntimeError):
    """Raised when the dashboard cannot fetch valid data from the backend API."""


class DashboardAPIClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        configured_url = (base_url or os.getenv("ELITEFOOTBALL_API_BASE_URL") or DEFAULT_API_BASE_URL).rstrip("/")
        self.base_url = configured_url
        self.base_urls = [configured_url]
        if not (base_url or os.getenv("ELITEFOOTBALL_API_BASE_URL")):
            self.base_urls.extend(FALLBACK_API_BASE_URLS)
        self.timeout_seconds = timeout_seconds

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        not_found_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        errors: list[str] = []
        for base_url in self.base_urls:
            url = f"{base_url}{path}"
            try:
                response = requests.get(url, params=params, timeout=self.timeout_seconds)
                response.raise_for_status()
            except requests.HTTPError as exc:
                status_code = exc.response.status_code if exc.response is not None else None
                if (
                    status_code == 422
                    and params is not None
                    and isinstance(params.get("limit"), int)
                    and params.get("limit", 0) > 100
                ):
                    retry_params = dict(params)
                    retry_params["limit"] = 100
                    try:
                        retry_response = requests.get(url, params=retry_params, timeout=self.timeout_seconds)
                        retry_response.raise_for_status()
                        payload = retry_response.json()
                        if not isinstance(payload, dict):
                            raise DashboardAPIError(f"Backend API returned an unexpected payload for {url}")
                        self.base_url = base_url
                        return payload
                    except requests.RequestException as retry_exc:
                        errors.append(f"{url}: {retry_exc}")
                        continue
                    except ValueError as retry_exc:
                        raise DashboardAPIError(f"Backend API returned invalid JSON for {url}") from retry_exc
                if status_code == 404 and not_found_payload is not None:
                    self.base_url = base_url
                    return dict(not_found_payload)
                errors.append(f"{url}: {exc}")
                continue
            except requests.RequestException as exc:
                errors.append(f"{url}: {exc}")
                continue

            try:
                payload = response.json()
            except ValueError as exc:
                raise DashboardAPIError(f"Backend API returned invalid JSON for {url}") from exc

            if not isinstance(payload, dict):
                raise DashboardAPIError(f"Backend API returned an unexpected payload for {url}")
            self.base_url = base_url
            return payload

        raise DashboardAPIError("Unable to reach backend API. Tried: " + " | ".join(errors))

    def get_health(self) -> dict[str, Any]:
        return self._get("/health")

    def get_dashboard_status(self) -> dict[str, Any]:
        return self._get("/dashboard/status")

    def get_players(
        self,
        *,
        name: str | None = None,
        position: str | None = None,
        club: str | None = None,
        include: str = "features,kpi,valuation",
        limit: int = 200,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._get(
            "/players",
            params={
                "name": name,
                "position": position,
                "club": club,
                "include": include,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_player_stats(self, player_name: str, *, limit: int = 20, offset: int = 0, sort: str = "-match_date") -> dict[str, Any]:
        return self._get(
            f"/players/{player_name}/stats",
            params={"limit": limit, "offset": offset, "sort": sort},
            not_found_payload={"player_name": player_name, "count": 0, "items": []},
        )

    def get_compare(self, player_name: str, *, limit: int = 5) -> dict[str, Any]:
        return self._get(
            "/compare",
            params={"player_name": player_name, "limit": limit},
            not_found_payload={
                "player_name": player_name,
                "position": None,
                "comparison_features": {},
                "similar_players": [],
            },
        )

    def get_value(
        self,
        *,
        player_name: str | None = None,
        tier: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        safe_limit = max(1, min(limit, 100))
        return self._get(
            "/value",
            params={
                "player_name": player_name,
                "tier": tier,
                "limit": safe_limit,
                "offset": offset,
            },
        )
