from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from occasion.engine.telegram import TelegramClient, TelegramError, delivery_messages


def package_fixture(root: Path) -> Path:
    card = root / "card.png"
    Image.new("RGB", (1080, 1350), "#223344").save(card)
    package = root / "package.json"
    package.write_text(
        json.dumps(
            {
                "jobKey": "dussehra:2026:metaldock",
                "event": {
                    "id": "dussehra",
                    "name": "Dussehra / Vijayadashami",
                    "date": "2026-10-20",
                },
                "brand": {"id": "metaldock", "name": "Metal Dock"},
                "draft": {
                    "captions": {
                        "linkedin": "LinkedIn copy",
                        "x": "X copy",
                        "google-business": "Google Business copy",
                    }
                },
                "artifacts": {"card": str(card)},
            }
        ),
        encoding="utf-8",
    )
    return package


class TelegramTests(unittest.TestCase):
    def test_delivery_messages_are_copy_ready_and_platform_separated(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            package = json.loads(package_fixture(Path(folder)).read_text(encoding="utf-8"))

            messages = delivery_messages(package)

            self.assertEqual(messages[0], "LINKEDIN\n\nLinkedIn copy")
            self.assertIn("X\n\nX copy", messages)
            self.assertIn("GOOGLE BUSINESS\n\nGoogle Business copy", messages)
            self.assertTrue(all(len(message) <= 3900 for message in messages))

    def test_delivery_sends_image_before_caption_blocks(self) -> None:
        calls: list[tuple[str, dict, Path | None]] = []

        def transport(method: str, fields: dict, file: Path | None):
            calls.append((method, fields, file))
            return {"ok": True}

        with tempfile.TemporaryDirectory() as folder:
            package = package_fixture(Path(folder))
            TelegramClient(token="token", chat_id="chat", transport=transport).deliver(package)

        self.assertEqual(calls[0][0], "sendPhoto")
        self.assertIsNotNone(calls[0][2])
        self.assertTrue(all(call[0] == "sendMessage" for call in calls[1:]))

    def test_telegram_rejection_is_a_loud_failure(self) -> None:
        def transport(method: str, fields: dict, file: Path | None):
            return {"ok": False, "description": "chat not found"}

        with tempfile.TemporaryDirectory() as folder:
            package = package_fixture(Path(folder))
            with self.assertRaisesRegex(TelegramError, "chat not found"):
                TelegramClient(token="token", chat_id="chat", transport=transport).deliver(package)


if __name__ == "__main__":
    unittest.main()
