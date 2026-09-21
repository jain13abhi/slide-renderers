from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from PIL import Image

from occasion.engine import load_registry, plan_jobs
from occasion.engine.pipeline import Draft, PipelineError, run_job


class FakeDrafter:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls = 0

    def draft(self, job) -> Draft:
        self.calls += 1
        return Draft.from_payload(self.payload, channels=job.brand.channels)


class FakeImageProvider:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls = 0

    def generate(self, *, prompt: str, destination: Path, job_key: str) -> Path:
        self.calls += 1
        if self.fail:
            raise PipelineError("image provider unavailable")
        Image.new("RGB", (1200, 1600), "#73523d").save(destination)
        return destination


def valid_draft() -> dict:
    return {
        "eyebrow": "VIJAYADASHAMI · 20 OCTOBER 2026",
        "greeting": "May every instrument of work serve a worthy beginning.",
        "tagline": "Wishing you a thoughtful Dussehra.",
        "imagePrompt": "A respectful Indian workplace prepared for Vijayadashami.",
        "captions": {
            "telegram": "A Telegram-ready caption.",
            "linkedin": "A LinkedIn-ready caption.",
            "instagram": "An Instagram-ready caption.",
            "facebook": "A Facebook-ready caption.",
            "threads": "A Threads-ready caption.",
            "x": "An X-ready caption without a URL.",
            "google-business": "A Google Business Profile update.",
        },
    }


class DraftTests(unittest.TestCase):
    def test_draft_requires_copy_for_every_configured_channel(self) -> None:
        payload = valid_draft()
        payload["captions"].pop("x")

        with self.assertRaisesRegex(PipelineError, "captions.x"):
            Draft.from_payload(payload, channels=("telegram", "x"))

    def test_x_caption_must_not_contain_a_url(self) -> None:
        payload = valid_draft()
        payload["captions"]["x"] = "Read more at https://example.com"

        with self.assertRaisesRegex(PipelineError, "must not contain a URL"):
            Draft.from_payload(payload, channels=("x",))


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        repository_root = Path(__file__).resolve().parents[2]
        registry = load_registry(
            repository_root / "occasion" / "registry.json",
            asset_root=repository_root,
        )
        self.job = next(
            job
            for job in plan_jobs(registry, as_of=date(2026, 10, 6), completed=set())
            if job.brand.id == "metaldock"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_success_writes_reproducible_package_and_completion_marker(self) -> None:
        result = run_job(
            self.job,
            drafter=FakeDrafter(valid_draft()),
            image_provider=FakeImageProvider(),
            output_root=self.root / "output",
            state_root=self.root / "state",
        )

        self.assertTrue(result.card.is_file())
        self.assertTrue(result.background.is_file())
        self.assertTrue(result.package.is_file())
        marker = self.root / "state" / "dussehra-2026-metaldock.json"
        self.assertTrue(marker.is_file())
        package = json.loads(result.package.read_text(encoding="utf-8"))
        self.assertEqual(package["jobKey"], "dussehra:2026:metaldock")
        self.assertEqual(package["draft"]["captions"]["x"], "An X-ready caption without a URL.")
        self.assertEqual(package["sources"], list(self.job.occurrence.sources))

    def test_failure_never_writes_completion_marker(self) -> None:
        with self.assertRaisesRegex(PipelineError, "unavailable"):
            run_job(
                self.job,
                drafter=FakeDrafter(valid_draft()),
                image_provider=FakeImageProvider(fail=True),
                output_root=self.root / "output",
                state_root=self.root / "state",
            )

        self.assertFalse((self.root / "state" / "dussehra-2026-metaldock.json").exists())


if __name__ == "__main__":
    unittest.main()
