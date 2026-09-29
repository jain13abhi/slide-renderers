from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from occasion.engine.cli import main


class MigratePathsTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path, Path, Path]:
        legacy_root = root / "slide-renderers"
        production_root = root / "data" / "occasion" / "production"
        package = production_root / "dussehra-2026" / "packages" / "dockfinity.json"
        card = production_root / "dussehra-2026" / "cards" / "dockfinity.png"
        package.parent.mkdir(parents=True)
        card.parent.mkdir(parents=True)
        card.write_bytes(b"png")
        package.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "jobKey": "dussehra:2026:dockfinity",
                    "artifacts": {
                        "card": r"..\data\occasion\production\dussehra-2026\cards\dockfinity.png"
                    },
                }
            ),
            encoding="utf-8",
        )
        state_root = root / "state"
        state_root.mkdir()
        marker = state_root / "dussehra-2026-dockfinity.json"
        marker.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "jobKey": "dussehra:2026:dockfinity",
                    "status": "generated",
                    "package": r"..\data\occasion\production\dussehra-2026\packages\dockfinity.json",
                }
            ),
            encoding="utf-8",
        )
        return legacy_root, production_root, state_root, marker

    def test_migration_is_dry_run_by_default_then_idempotent_when_written(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            legacy_root, production_root, state_root, marker = self._fixture(Path(folder))
            original = marker.read_text(encoding="utf-8")

            dry_run = main(
                [
                    "migrate-paths",
                    "--repo-root",
                    str(legacy_root),
                    "--state-root",
                    str(state_root),
                    "--output-root",
                    str(production_root),
                ]
            )

            self.assertEqual(dry_run, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), original)

            first_write = main(
                [
                    "migrate-paths",
                    "--repo-root",
                    str(legacy_root),
                    "--state-root",
                    str(state_root),
                    "--output-root",
                    str(production_root),
                    "--write",
                ]
            )
            first_payload = json.loads(marker.read_text(encoding="utf-8"))
            package = production_root / first_payload["package"]
            package_payload = json.loads(package.read_text(encoding="utf-8"))

            self.assertEqual(first_write, 0)
            self.assertEqual(first_payload["schemaVersion"], 2)
            self.assertEqual(
                first_payload["package"], "dussehra-2026/packages/dockfinity.json"
            )
            self.assertEqual(package_payload["schemaVersion"], 2)
            self.assertEqual(
                package_payload["artifacts"]["card"],
                "dussehra-2026/cards/dockfinity.png",
            )
            self.assertNotIn("\\", marker.read_text(encoding="utf-8"))
            self.assertNotIn("\\", package.read_text(encoding="utf-8"))

            before_second_write = marker.read_text(encoding="utf-8")
            second_write = main(
                [
                    "migrate-paths",
                    "--repo-root",
                    str(legacy_root),
                    "--state-root",
                    str(state_root),
                    "--output-root",
                    str(production_root),
                    "--write",
                ]
            )

            self.assertEqual(second_write, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), before_second_write)


if __name__ == "__main__":
    unittest.main()
