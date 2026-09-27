from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from urllib.error import HTTPError

from PIL import Image

from occasion.engine import GenerationBudget, load_registry, plan_jobs
from occasion.engine.pipeline import PipelineError
from occasion.engine.providers import GeminiDrafter, HiggsfieldProvider

from occasion.tests.test_pipeline import valid_draft


class ProviderTestCase(unittest.TestCase):
    def setUp(self) -> None:
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


class GeminiTests(ProviderTestCase):
    @staticmethod
    def _http_error(code: int, message: str, *, retry_after: str | None = None) -> HTTPError:
        headers = {"Retry-After": retry_after} if retry_after is not None else {}
        body = json.dumps({"error": {"code": code, "message": message}}).encode("utf-8")
        return HTTPError(
            "https://generativelanguage.googleapis.com/test",
            code,
            message,
            headers,
            BytesIO(body),
        )

    def test_http_transport_retries_429_then_returns_text(self) -> None:
        delays: list[float] = []
        success = mock.MagicMock()
        success.__enter__.return_value.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "Recovered"}]}}]}
        ).encode("utf-8")

        drafter = GeminiDrafter(
            api_key="test-key",
            retry_attempts=3,
            retry_base_seconds=0,
            sleep=delays.append,
        )
        with mock.patch(
            "occasion.engine.providers.request.urlopen",
            side_effect=[self._http_error(429, "Temporary quota", retry_after="0"), success],
        ) as urlopen:
            result = drafter._transport({"contents": []})

        self.assertEqual(result, "Recovered")
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(delays, [0])

    def test_http_transport_reports_quota_detail_after_bounded_retries(self) -> None:
        delays: list[float] = []
        errors = [self._http_error(429, "Free-tier daily quota exhausted") for _ in range(3)]
        drafter = GeminiDrafter(
            api_key="test-key",
            retry_attempts=3,
            retry_base_seconds=0,
            sleep=delays.append,
        )

        with mock.patch("occasion.engine.providers.request.urlopen", side_effect=errors) as urlopen:
            with self.assertRaisesRegex(PipelineError, "Free-tier daily quota exhausted"):
                drafter._transport({"contents": []})

        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(delays, [0, 0])

    def test_http_transport_does_not_retry_non_transient_400(self) -> None:
        delays: list[float] = []
        drafter = GeminiDrafter(
            api_key="test-key",
            retry_attempts=3,
            retry_base_seconds=0,
            sleep=delays.append,
        )

        with mock.patch(
            "occasion.engine.providers.request.urlopen",
            side_effect=self._http_error(400, "Invalid request"),
        ) as urlopen:
            with self.assertRaisesRegex(PipelineError, "Invalid request"):
                drafter._transport({"contents": []})

        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(delays, [])

    def test_research_runs_once_and_invalid_draft_gets_one_bounded_correction(self) -> None:
        calls: list[dict] = []
        responses = iter(["Grounded research packet", "{}", json.dumps(valid_draft())])

        def transport(body: dict) -> str:
            calls.append(body)
            return next(responses)

        drafter = GeminiDrafter(transport=transport)

        draft = drafter.draft(self.job)

        self.assertEqual(draft.eyebrow, valid_draft()["eyebrow"])
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0]["tools"], [{"google_search": {}}])
        self.assertNotIn("responseMimeType", calls[0].get("generationConfig", {}))
        self.assertEqual(calls[1]["generationConfig"]["responseMimeType"], "application/json")
        self.assertEqual(calls[2]["generationConfig"]["responseMimeType"], "application/json")

    def test_two_invalid_drafts_fail_without_a_third_drafting_call(self) -> None:
        calls: list[dict] = []

        def transport(body: dict) -> str:
            calls.append(body)
            return "Research" if len(calls) == 1 else "{}"

        with self.assertRaisesRegex(PipelineError, "two drafting attempts"):
            GeminiDrafter(transport=transport).draft(self.job)

        self.assertEqual(len(calls), 3)


class HiggsfieldTests(ProviderTestCase):
    def test_provider_checks_account_generates_once_and_downloads_completed_image(self) -> None:
        commands: list[list[str]] = []

        def run(command: list[str]):
            commands.append(command)
            if command[1:3] == ["account", "status"]:
                return SimpleNamespace(returncode=0, stdout='{"credits": 100}', stderr="")
            return SimpleNamespace(
                returncode=0,
                stdout='{"status":"completed","result_url":"https://cdn.example/art.png"}',
                stderr="",
            )

        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample.png"
            Image.new("RGB", (1200, 1600), "#554433").save(sample)
            image_bytes = sample.read_bytes()
            provider = HiggsfieldProvider(
                run_command=run,
                download=lambda url: image_bytes,
                budget=GenerationBudget(max_attempts=2),
            )
            output = Path(folder) / "result.png"

            provider.generate(prompt="Culturally accurate scene", destination=output, job_key=self.job.key)

            self.assertEqual(len(commands), 2)
            self.assertEqual(commands[0][:3], ["higgsfield", "account", "status"])
            self.assertEqual(commands[1][:3], ["higgsfield", "generate", "create"])
            with Image.open(output) as image:
                self.assertEqual(image.size, (1200, 1600))

    def test_authentication_failure_stops_before_generation(self) -> None:
        commands: list[list[str]] = []

        def run(command: list[str]):
            commands.append(command)
            return SimpleNamespace(returncode=1, stdout="", stderr="Not authenticated")

        provider = HiggsfieldProvider(
            run_command=run,
            download=lambda url: b"",
            budget=GenerationBudget(max_attempts=2),
        )
        with self.assertRaisesRegex(PipelineError, "authentication"):
            provider.generate(
                prompt="Scene", destination=Path("unused.png"), job_key=self.job.key
            )

        self.assertEqual(len(commands), 1)


if __name__ == "__main__":
    unittest.main()
