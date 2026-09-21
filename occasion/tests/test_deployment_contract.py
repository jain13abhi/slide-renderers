from __future__ import annotations

import re
import unittest
from pathlib import Path


class DeploymentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[2]
        cls.workflow = (root / "occasion" / "deployment" / "occasion-production.yml").read_text(
            encoding="utf-8"
        )

    def test_template_uses_only_the_private_desktop_runner_and_has_no_pr_trigger(self) -> None:
        self.assertIn(
            "runs-on: [self-hosted, windows, x64, dock-content-desktop]",
            self.workflow,
        )
        self.assertNotRegex(self.workflow, re.compile(r"^\s*pull_request:", re.MULTILINE))
        self.assertNotIn("ubuntu-latest", self.workflow)
        self.assertNotIn("dock-content-vps", self.workflow)
        self.assertGreaterEqual(self.workflow.count("shell: powershell"), 5)

    def test_apps_script_dispatch_and_github_schedule_are_both_supported(self) -> None:
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("schedule:", self.workflow)
        self.assertIn("inputs.date", self.workflow)

    def test_generated_assets_are_committed_before_telegram_delivery(self) -> None:
        commit_position = self.workflow.index("Commit generated package")
        delivery_position = self.workflow.index("Deliver package to Telegram")
        self.assertLess(commit_position, delivery_position)
        self.assertIn("notify-failure", self.workflow)

    def test_partial_success_is_archived_and_delivered_without_regeneration(self) -> None:
        self.assertIn("id: archive", self.workflow)
        self.assertIn(
            "if: always() && steps.checkout_engine.outcome == 'success' && steps.produce.outcome != 'skipped'",
            self.workflow,
        )
        self.assertIn(
            "if: always() && steps.archive.outcome == 'success' && steps.produce.outcome != 'skipped'",
            self.workflow,
        )

    def test_windows_preflight_uses_powershell_safe_python_quoting(self) -> None:
        self.assertIn("id: preflight", self.workflow)
        self.assertIn(
            'python -c "from PIL import Image; print(\'Pillow\', Image.__version__)"',
            self.workflow,
        )

    def test_failure_notification_reports_the_actual_failed_stage(self) -> None:
        self.assertIn("steps.preflight.outcome == 'failure'", self.workflow)
        self.assertIn("steps.produce.outcome == 'failure'", self.workflow)
        self.assertIn("steps.archive.outcome == 'failure'", self.workflow)

    def test_higgsfield_and_gemini_credentials_are_not_hardcoded(self) -> None:
        self.assertIn("secrets.GEMINI_API_KEY", self.workflow)
        self.assertNotRegex(self.workflow, re.compile(r"AIza[0-9A-Za-z_-]{20,}"))
        self.assertNotIn("HIGGSFIELD_API_KEY", self.workflow)

    def test_generated_content_stays_private_without_cross_repository_token(self) -> None:
        self.assertIn("permissions:\n  contents: write", self.workflow)
        self.assertIn("data/occasion/production", self.workflow)
        self.assertIn("data/occasion/state", self.workflow)
        self.assertNotIn("SLIDE_RENDERERS_TOKEN", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)


if __name__ == "__main__":
    unittest.main()
