from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from occasion.engine.cli import main


class CliTests(unittest.TestCase):
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
