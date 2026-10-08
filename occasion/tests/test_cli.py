from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from occasion.engine.cli import main


class CliTests(unittest.TestCase):
    def test_discover_cli_archives_report_and_produce_uses_its_calendar(self):
        root = Path(__file__).resolve().parents[2]
        from occasion.engine.discovery import SourceDocument
        with tempfile.TemporaryDirectory() as folder:
            calendar = Path(folder) / "calendar"
            doc = SourceDocument("https://www.surveyofindia.gov.in/UserFiles/files/list%20of%20holidays-2026.pdf",
                                 "GAZETTED HOLIDAYS DURING THE YEAR 2026\n13. Mahatma Gandhi's Birthday October, 02 Asvina 10 Friday")
            with patch("occasion.engine.discovery.fetch_official", return_value=doc), \
                 patch("occasion.engine.cli.GeminiDrafter") as drafter:
                drafter.return_value.research_calendar.return_value = '{"events":[]}'
                code = main(["discover", "--date", "2026-10-02", "--repo-root", str(root),
                             "--calendar-root", str(calendar)])
            self.assertEqual(code, 0)
            manifest = Path(folder) / "manifest.json"
            self.assertEqual(main(["produce", "--date", "2026-10-02", "--repo-root", str(root),
                                   "--registry", str(calendar / "registry.json"), "--dry-run",
                                   "--state-root", str(Path(folder) / "state"), "--manifest", str(manifest)]), 0)
            self.assertEqual(len(json.loads(manifest.read_text())["planned"]), 3)

    def test_batch_mode_defers_excess_jobs_instead_of_aborting_all(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "manifest.json"
            self.assertEqual(main(["produce", "--date", "2026-10-06", "--repo-root", str(root),
                                   "--max-jobs", "1", "--batch", "--dry-run",
                                   "--state-root", str(Path(folder) / "state"), "--manifest", str(manifest)]), 0)
            self.assertEqual(len(json.loads(manifest.read_text())["planned"]), 1)

    def test_degraded_calendar_alert_is_sent_once_and_retained_on_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "2026-10-02.json"
            report.write_text(json.dumps({"date": "2026-10-02", "warnings": ["source failed"]}))
            with patch("occasion.engine.cli._telegram_from_environment") as factory:
                self.assertEqual(main(["calendar-health", "--report", str(report)]), 1)
                self.assertEqual(main(["calendar-health", "--report", str(report)]), 1)
                factory.return_value.send_message.assert_called_once()

    def test_calendar_alert_failure_does_not_mark_the_warning_sent(self):
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "2026-10-02.json"
            report.write_text(json.dumps({"date": "2026-10-02", "warnings": ["source failed"]}))
            with patch("occasion.engine.cli._telegram_from_environment") as factory:
                factory.return_value.send_message.side_effect = RuntimeError("Telegram unavailable")
                with self.assertRaisesRegex(RuntimeError, "Telegram unavailable"):
                    main(["calendar-health", "--report", str(report)])
            self.assertNotIn("alerted", json.loads(report.read_text()))

    def test_desktop_written_state_makes_produce_and_deliver_zero_event(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=repository_root.parent) as folder:
            root = Path(folder)
            production_root = root / "production"
            state_root = root / "state"
            package = production_root / "legacy" / "package.json"
            package.parent.mkdir(parents=True)
            package.write_text("{}", encoding="utf-8")
            state_root.mkdir()
            windows_relative = os.path.relpath(package, repository_root).replace("/", "\\")
            for job_key in ("dussehra:2026:dockfinity", "dussehra:2026:metaldock"):
                marker_name = job_key.replace(":", "-") + ".json"
                (state_root / marker_name).write_text(
                    json.dumps(
                        {
                            "schemaVersion": 1,
                            "jobKey": job_key,
                            "status": "delivered",
                            "package": windows_relative,
                        }
                    ),
                    encoding="utf-8",
                )
            manifest = root / "manifest.json"

            produce_code = main(
                [
                    "produce",
                    "--date",
                    "2026-10-06",
                    "--repo-root",
                    str(repository_root),
                    "--state-root",
                    str(state_root),
                    "--output-root",
                    str(production_root),
                    "--manifest",
                    str(manifest),
                ]
            )
            deliver_code = main(
                [
                    "deliver",
                    "--repo-root",
                    str(repository_root),
                    "--state-root",
                    str(state_root),
                    "--output-root",
                    str(production_root),
                ]
            )

            self.assertEqual(produce_code, 0)
            self.assertEqual(deliver_code, 0)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["planned"], [])

    def test_dry_run_plans_without_requiring_any_credentials(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "manifest.json"

            code = main(
                [
                    "produce",
                    "--date",
                    "2026-10-06",
                    "--dry-run",
                    "--repo-root",
                    str(repository_root),
                    "--state-root",
                    str(Path(folder) / "state"),
                    "--manifest",
                    str(manifest),
                ]
            )

            self.assertEqual(code, 0)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(
                [item["jobKey"] for item in payload["planned"]],
                ["dussehra:2026:dockfinity", "dussehra:2026:metaldock"],
            )
            self.assertEqual(payload["produced"], [])

    def test_job_limit_stops_before_credentials_or_generation(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError, "job limit"):
                main(
                    [
                        "produce",
                        "--date",
                        "2026-10-06",
                        "--repo-root",
                        str(repository_root),
                        "--state-root",
                        str(Path(folder) / "state"),
                        "--manifest",
                        str(Path(folder) / "manifest.json"),
                        "--max-jobs",
                        "1",
                    ]
                )


if __name__ == "__main__":
    unittest.main()
