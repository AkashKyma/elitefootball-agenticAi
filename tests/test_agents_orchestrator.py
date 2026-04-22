import unittest
from unittest.mock import Mock, patch

from app.agents.orchestrator import AGENT_HANDLERS, build_agent_summary, route_task, run_task, supported_task_kinds
from app.agents.report_generator_agent import run as run_report_generator
from app.agents.types import AgentStepResult, AgentTask


class TestAgentsOrchestrator(unittest.TestCase):
    def test_supported_task_kinds_and_summary(self):
        self.assertEqual(
            supported_task_kinds(),
            ["clean_data", "full_refresh", "generate_report", "run_analysis", "scrape_players"],
        )
        summary = build_agent_summary()
        agent_names = [row["name"] for row in summary]
        self.assertIn("coordinator", agent_names)
        self.assertIn("scraper", agent_names)
        self.assertIn("data_cleaner", agent_names)
        self.assertIn("analyst", agent_names)
        self.assertIn("report_generator", agent_names)

    def test_route_task(self):
        self.assertEqual(route_task("scrape_players"), ["scraper"])
        self.assertEqual(route_task("full_refresh"), ["scraper", "data_cleaner", "analyst", "report_generator"])

    def test_unsupported_task_raises(self):
        with self.assertRaises(ValueError):
            route_task("unknown_task")

    def test_full_refresh_route_order_and_context(self):
        mock_scraper = Mock(
            return_value=AgentStepResult(
                agent_name="scraper",
                task_kind="full_refresh",
                status="ok",
                summary="scraper done",
                artifacts={"scrape_plan": {"scope": "IDV players"}},
            )
        )
        mock_cleaner = Mock(
            return_value=AgentStepResult(
                agent_name="data_cleaner",
                task_kind="full_refresh",
                status="ok",
                summary="cleaner done",
                artifacts={
                    "silver": {"tables": {"players": [{"player_name": "John Doe"}], "player_match_stats": []}},
                    "gold": {"tables": {"player_features": [{"player_name": "John Doe"}]}},
                },
            )
        )
        mock_analyst = Mock(
            return_value=AgentStepResult(
                agent_name="analyst",
                task_kind="full_refresh",
                status="ok",
                summary="analyst done",
                artifacts={"valuation": {"rows": [{"player_name": "John Doe"}]}, "similarity": {"rows": []}},
            )
        )
        mock_report = Mock(
            return_value=AgentStepResult(
                agent_name="report_generator",
                task_kind="full_refresh",
                status="ok",
                summary="report done",
                artifacts={"report": {"player_count": 1}},
            )
        )

        with patch.dict(
            AGENT_HANDLERS,
            {
                "scraper": mock_scraper,
                "data_cleaner": mock_cleaner,
                "analyst": mock_analyst,
                "report_generator": mock_report,
            },
        ):
            result = run_task(AgentTask.from_input("full_refresh"))

        self.assertEqual(result.route, ["scraper", "data_cleaner", "analyst", "report_generator"])
        self.assertEqual([step.agent_name for step in result.steps], result.route)
        self.assertEqual(result.status, "ok")
        self.assertIn("scraper done", result.summary)

        analyst_task = mock_analyst.call_args.args[0]
        report_task = mock_report.call_args.args[0]
        self.assertEqual(analyst_task.metadata["silver_tables"]["players"][0]["player_name"], "John Doe")
        self.assertIn("valuation", report_task.metadata["analysis_outputs"])

    def test_report_generator_output_is_deterministic(self):
        task = AgentTask.from_input(
            "generate_report",
            metadata={
                "silver_tables": {"players": [{"player_name": "A"}, {"player_name": "B"}], "player_match_stats": [{}, {}, {}]},
                "analysis_outputs": {
                    "kpi": {"rows": [{}, {}]},
                    "risk": {"rows": [{}]},
                },
            },
        )
        result = run_report_generator(task)
        self.assertEqual(result.artifacts["report"]["player_count"], 2)
        self.assertEqual(result.artifacts["report"]["match_stat_count"], 3)
        self.assertEqual(result.artifacts["report"]["analysis_artifact_counts"], {"kpi": 2, "risk": 1})


if __name__ == "__main__":
    unittest.main()
