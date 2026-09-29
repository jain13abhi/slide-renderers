from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from occasion.engine.cli import main


class CliTests(unittest.TestCase):
    def test_desktop_written_state_makes_produce_and_deliver_zero_event(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as folder:
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
