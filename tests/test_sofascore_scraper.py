import unittest

from app.scraping.sofascore import _map_player_stat_row


class TestSofascoreScraper(unittest.TestCase):
    def test_maps_lineup_row_to_player_match_stats(self):
        event = {
            "id": 12345,
            "startTimestamp": 1714300000,
            "homeTeam": {"id": 39723, "name": "Independiente del Valle"},
            "awayTeam": {"id": 100, "name": "Opponent FC"},
        }
        player_row = {
            "teamId": 39723,
            "player": {"name": "Test Player"},
            "statistics": {
                "minutesPlayed": 90,
                "goals": 1,
                "goalAssist": 1,
                "totalShots": 3,
                "accuratePass": 42,
                "yellowCards": 1,
                "redCards": 0,
                "expectedGoals": 0.44,
                "expectedAssists": 0.21,
                "accurateFinalThirdPasses": 9,
                "dribblesSucceeded": 4,
                "touches": 65,
            },
        }

        mapped = _map_player_stat_row(team_id=39723, event_id=12345, event=event, player_row=player_row)
        assert mapped is not None
        self.assertEqual(mapped["source"], "sofascore")
        self.assertEqual(mapped["player_name"], "Test Player")
        self.assertEqual(mapped["goals"], 1)
        self.assertEqual(mapped["assists"], 1)
        self.assertEqual(mapped["shots"], 3)
        self.assertEqual(mapped["passes_completed"], 42)
        self.assertEqual(mapped["xg"], 0.44)
        self.assertEqual(mapped["xa"], 0.21)
        self.assertEqual(mapped["progressive_passes"], 9)


if __name__ == "__main__":
    unittest.main()
