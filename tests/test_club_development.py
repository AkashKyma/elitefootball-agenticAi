import unittest

from app.analysis.club_development import build_club_development_rankings, normalize_club_name


class TestClubDevelopment(unittest.TestCase):
    def test_normalize_club_name(self):
        self.assertEqual(normalize_club_name("Independiente del Valle"), "IDV")
        self.assertEqual(normalize_club_name("SL Benfica"), "Benfica")
        self.assertEqual(normalize_club_name("AFC Ajax"), "Ajax")
        self.assertIsNone(normalize_club_name(None))

    def test_build_rankings_with_sparse_inputs(self):
        result = build_club_development_rankings(
            silver_tables={"players": [], "transfers": []},
            gold_tables={"player_features": []},
            kpi_rows=[],
            valuation_rows=[],
        )

        self.assertTrue(result["path"].endswith("club_development_rankings.json"))
        self.assertEqual([row["club_name"] for row in result["rankings"]], ["IDV", "Benfica", "Ajax"])
        for row in result["rankings"]:
            self.assertEqual(row["overall_score"], 0.0)
            self.assertEqual(row["confidence_score"], 0.0)
            self.assertIn("low_evidence", row["notes"])

    def test_build_rankings_prefers_club_with_better_development_and_resale_inputs(self):
        silver_tables = {
            "players": [
                {"player_name": "Young IDV", "date_of_birth": "2005-01-01", "current_club": "Independiente del Valle"},
                {"player_name": "Prime Benfica", "date_of_birth": "2003-01-01", "current_club": "SL Benfica"},
                {"player_name": "Ajax Talent", "date_of_birth": "2004-01-01", "current_club": "AFC Ajax"},
            ],
            "transfers": [
                {"from_club": "SL Benfica", "to_club": "Premier League Club", "player_name": "Sold One", "league": "Premier League"},
                {"from_club": "SL Benfica", "to_club": "Serie A Club", "player_name": "Sold Two", "league": "Serie A"},
                {"from_club": "AFC Ajax", "to_club": "La Liga Club", "player_name": "Sold Three", "league": "La Liga"},
            ],
        }
        gold_tables = {
            "player_features": [
                {"player_name": "Young IDV", "current_club": "Independiente del Valle", "minutes": 1600},
                {"player_name": "Prime Benfica", "current_club": "SL Benfica", "minutes": 2100},
                {"player_name": "Ajax Talent", "current_club": "AFC Ajax", "minutes": 1900},
            ]
        }
        kpi_rows = [
            {"player_name": "Young IDV", "base_kpi_score": 4.0, "minutes_played": 1600},
            {"player_name": "Prime Benfica", "base_kpi_score": 5.8, "minutes_played": 2100},
            {"player_name": "Ajax Talent", "base_kpi_score": 5.0, "minutes_played": 1900},
        ]
        valuation_rows = [
            {"player_name": "Young IDV", "current_club": "Independiente del Valle", "valuation_score": 62.0, "inputs": {"age": 20}},
            {"player_name": "Prime Benfica", "current_club": "SL Benfica", "valuation_score": 80.0, "inputs": {"age": 22}},
            {"player_name": "Ajax Talent", "current_club": "AFC Ajax", "valuation_score": 74.0, "inputs": {"age": 21}},
        ]

        result = build_club_development_rankings(silver_tables, gold_tables, kpi_rows, valuation_rows)
        rankings = result["rankings"]

        self.assertEqual(rankings[0]["club_name"], "Benfica")
        self.assertGreater(rankings[0]["resale_score"], rankings[1]["resale_score"])
        self.assertGreater(rankings[0]["development_score"], rankings[2]["development_score"])
        self.assertEqual(rankings[0]["rank"], 1)

        ajax_row = next(row for row in rankings if row["club_name"] == "Ajax")
        idv_row = next(row for row in rankings if row["club_name"] == "IDV")
        self.assertGreater(ajax_row["overall_score"], idv_row["overall_score"])
        self.assertGreater(rankings[0]["confidence_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
