import unittest
from unittest.mock import Mock, patch

from app.scraping.tavily import build_source_queue, classify_source_url, discover_idv_source_urls
from app.config import settings


class TestTavilyDiscovery(unittest.TestCase):
    def test_returns_unconfigured_when_api_key_missing(self):
        previous_enabled = settings.tavily_enabled
        previous_key = settings.tavily_api_key
        object.__setattr__(settings, "tavily_enabled", True)
        object.__setattr__(settings, "tavily_api_key", None)
        try:
            payload = discover_idv_source_urls()
        finally:
            object.__setattr__(settings, "tavily_enabled", previous_enabled)
            object.__setattr__(settings, "tavily_api_key", previous_key)

        self.assertEqual(payload["status"], "unconfigured")
        self.assertEqual(payload["urls"], [])

    @patch("app.scraping.tavily.requests.post")
    def test_filters_results_to_supported_domains(self, mock_post):
        previous_enabled = settings.tavily_enabled
        previous_key = settings.tavily_api_key
        object.__setattr__(settings, "tavily_enabled", True)
        object.__setattr__(settings, "tavily_api_key", "test-key")
        try:
            response = Mock()
            response.json.return_value = {
                "results": [
                    {"url": "https://www.transfermarkt.com/independiente-del-valle/kader/verein/19309", "title": "TM"},
                    {"url": "https://fbref.com/en/squads/990519b8/Independiente-del-Valle-Stats", "title": "FBref"},
                    {"url": "https://example.com/not-allowed", "title": "Other"},
                ]
            }
            response.raise_for_status.return_value = None
            mock_post.return_value = response

            payload = discover_idv_source_urls()
        finally:
            object.__setattr__(settings, "tavily_enabled", previous_enabled)
            object.__setattr__(settings, "tavily_api_key", previous_key)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["urls"]), 2)
        self.assertTrue(any("transfermarkt.com" in url for url in payload["urls"]))
        self.assertTrue(any("fbref.com" in url for url in payload["urls"]))
        self.assertEqual(len(payload["source_queue"]), 2)
        self.assertTrue(any(row["runnable"] for row in payload["source_queue"]))

    def test_classifies_and_prioritizes_source_queue(self):
        queue = build_source_queue(
            [
                "https://www.transfermarkt.com/independiente-del-valle/startseite/verein/19309",
                "https://fbref.com/en/squads/990519b8/Independiente-del-Valle-Stats",
            ]
        )
        self.assertEqual(queue[0]["source_type"], "transfermarkt_club_page")
        self.assertTrue(queue[0]["runnable"])
        self.assertTrue(str(queue[0]["runnable_url"]).endswith("/independiente-del-valle/kader/verein/19309"))
        self.assertEqual(queue[1]["source_type"], "fbref_stats")
        self.assertFalse(queue[1]["runnable"])

    def test_classify_source_url_transfermarkt_player(self):
        classified = classify_source_url("https://www.transfermarkt.com/test/profil/spieler/123")
        self.assertEqual(classified["source_name"], "transfermarkt")
        self.assertEqual(classified["source_type"], "transfermarkt_player")
        self.assertTrue(classified["runnable"])


if __name__ == "__main__":
    unittest.main()
