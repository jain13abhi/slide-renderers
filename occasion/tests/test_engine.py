from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from occasion.engine import (
    ConfigurationError,
    GenerationBudget,
    build_higgsfield_command,
    load_registry,
    parse_higgsfield_result,
    plan_jobs,
)


def registry_fixture() -> dict:
    return {
        "version": 1,
        "defaults": {"leadDays": 14, "maxImageAttempts": 2},
        "brands": [
            {
                "id": "metal",
                "name": "Metal",
                "enabled": True,
                "logo": "assets/metal.png",
                "rendererProfile": {
                    "accent": "#f6c344",
                    "text": "#ffffff",
                    "overlay": "#111111",
                },
                "channels": ["telegram", "linkedin"],
            },
            {
                "id": "future",
                "name": "Future",
                "enabled": False,
                "logo": "assets/future.png",
                "rendererProfile": {
                    "accent": "#ffffff",
                    "text": "#ffffff",
                    "overlay": "#000000",
                },
                "channels": ["telegram"],
            },
        ],
        "events": [
            {
                "id": "festival",
                "name": "Festival",
                "category": "religious",
                "tradition": "Confirmed tradition",
                "brandIds": ["metal", "future"],
                "imageDirection": "A culturally accurate, text-free scene.",
                "sensitivity": "standard",
            },
            {
                "id": "sensitive-event",
                "name": "Sensitive",
                "category": "political",
                "tradition": "Official national observance",
                "brandIds": ["metal"],
                "imageDirection": "Documentary still without party symbols.",
                "sensitivity": "approval-required",
            },
        ],
        "occurrences": [
            {
                "eventId": "festival",
                "date": "2026-10-20",
                "status": "locked",
                "verifiedAt": "2026-09-20",
                "sources": ["https://example.gov/calendar"],
            },
            {
                "eventId": "sensitive-event",
                "date": "2026-10-21",
                "status": "locked",
                "verifiedAt": "2026-09-20",
                "sources": ["https://example.gov/notice"],
            },
        ],
    }


class RegistryTests(unittest.TestCase):
    def test_repository_registry_is_valid_and_dussehra_is_locked(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]

        registry = load_registry(
            repository_root / "occasion" / "registry.json",
            asset_root=repository_root,
        )
        jobs = plan_jobs(registry, as_of=date(2026, 10, 6), completed=set())

        self.assertEqual(
            [job.key for job in jobs],
            ["dussehra:2026:dockfinity", "dussehra:2026:metaldock"],
        )

    def test_load_registry_validates_and_indexes_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "assets").mkdir()
            (root / "assets" / "metal.png").write_bytes(b"logo")
            (root / "registry.json").write_text(
                json.dumps(registry_fixture()), encoding="utf-8"
            )

            registry = load_registry(root / "registry.json", asset_root=root)

            self.assertEqual(registry.brands["metal"].name, "Metal")
            self.assertEqual(registry.events["festival"].category, "religious")
            self.assertEqual(registry.lead_days, 14)

    def test_enabled_brand_requires_an_existing_logo(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "registry.json").write_text(
                json.dumps(registry_fixture()), encoding="utf-8"
            )

            with self.assertRaisesRegex(ConfigurationError, "logo"):
                load_registry(root / "registry.json", asset_root=root)

    def test_occurrence_requires_a_real_source_and_locked_date(self) -> None:
        data = registry_fixture()
        data["occurrences"][0]["sources"] = []
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "assets").mkdir()
            (root / "assets" / "metal.png").write_bytes(b"logo")
            (root / "registry.json").write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ConfigurationError, "source"):
                load_registry(root / "registry.json", asset_root=root)


class PlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        (self.root / "assets" / "metal.png").write_bytes(b"logo")
        (self.root / "registry.json").write_text(
            json.dumps(registry_fixture()), encoding="utf-8"
        )
        self.registry = load_registry(self.root / "registry.json", asset_root=self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_plans_only_enabled_standard_brands_inside_lead_window(self) -> None:
        jobs = plan_jobs(self.registry, as_of=date(2026, 10, 6), completed=set())

        self.assertEqual([job.key for job in jobs], ["festival:2026:metal"])
        self.assertEqual(jobs[0].publish_date.isoformat(), "2026-10-20")

    def test_skips_duplicates_and_dates_outside_window(self) -> None:
        duplicate = {"festival:2026:metal"}

        jobs = plan_jobs(self.registry, as_of=date(2026, 10, 5), completed=duplicate)

        self.assertEqual(jobs, [])

    def test_sensitive_events_never_enter_unattended_generation(self) -> None:
        jobs = plan_jobs(self.registry, as_of=date(2026, 10, 7), completed=set())

        self.assertNotIn("sensitive-event:2026:metal", [job.key for job in jobs])


class HiggsfieldContractTests(unittest.TestCase):
    def test_command_is_noninteractive_image_only_and_machine_readable(self) -> None:
        command = build_higgsfield_command(
            model="nano_banana_2",
            prompt="A workshop prepared for a festival",
            aspect_ratio="4:5",
            resolution="2k",
        )

        self.assertEqual(command[:3], ["higgsfield", "generate", "create"])
        self.assertIn("--wait", command)
        self.assertIn("--json", command)
        self.assertIn("text-free", command[command.index("--prompt") + 1].lower())
        self.assertNotIn("--batch_size", command)

    def test_result_parser_accepts_nested_result_url(self) -> None:
        payload = json.dumps({"job": {"status": "completed", "result_url": "https://cdn.example/image.png"}})

        self.assertEqual(parse_higgsfield_result(payload), "https://cdn.example/image.png")

    def test_result_parser_rejects_non_https_or_incomplete_output(self) -> None:
        with self.assertRaisesRegex(ValueError, "completed HTTPS image"):
            parse_higgsfield_result('{"status":"queued","result_url":"http://bad"}')

    def test_budget_allows_one_retry_but_never_a_third_generation(self) -> None:
        budget = GenerationBudget(max_attempts=2)

        budget.record_attempt("festival:2026:metal")
        budget.record_attempt("festival:2026:metal")

        with self.assertRaisesRegex(RuntimeError, "generation budget"):
            budget.record_attempt("festival:2026:metal")


if __name__ == "__main__":
    unittest.main()
