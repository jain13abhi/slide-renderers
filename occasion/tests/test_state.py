from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from occasion.engine.state import StateError, load_state, mark_delivered, pending_delivery


class StateTests(unittest.TestCase):
    def test_generated_package_is_resumable_without_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / "output" / "package.json"
            package.parent.mkdir()
            package.write_text('{"jobKey":"event:2026:brand"}', encoding="utf-8")
            marker = root / "state" / "event-2026-brand.json"
            marker.parent.mkdir()
            marker.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "jobKey": "event:2026:brand",
                        "status": "generated",
                        "package": str(package),
                    }
                ),
                encoding="utf-8",
            )

            snapshot = load_state(root / "state")

            self.assertEqual(snapshot.produced, {"event:2026:brand"})
            self.assertEqual(snapshot.delivered, set())
            self.assertEqual(pending_delivery(snapshot), [("event:2026:brand", package)])

    def test_delivery_transition_is_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / "package.json"
            package.write_text('{"jobKey":"event:2026:brand"}', encoding="utf-8")
            marker = root / "state" / "event-2026-brand.json"
            marker.parent.mkdir()
            marker.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "jobKey": "event:2026:brand",
                        "status": "generated",
                        "package": str(package),
                    }
                ),
                encoding="utf-8",
            )

            mark_delivered(marker)
            mark_delivered(marker)

            payload = json.loads(marker.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "delivered")
            self.assertIn("deliveredAt", payload)

    def test_corrupt_marker_fails_closed_to_prevent_duplicate_credit_use(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            root.mkdir(exist_ok=True)
            (root / "broken.json").write_text("not json", encoding="utf-8")

            with self.assertRaisesRegex(StateError, "broken.json"):
                load_state(root)


if __name__ == "__main__":
    unittest.main()
