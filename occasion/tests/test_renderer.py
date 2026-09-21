from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from occasion.engine import Brand, RendererProfile
from occasion.engine.renderer import RenderError, render_card


class RendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.background = self.root / "background.png"
        self.logo = self.root / "logo.png"
        Image.new("RGB", (1600, 900), "#8c4f32").save(self.background)
        Image.new("RGBA", (500, 180), (255, 255, 255, 220)).save(self.logo)
        self.brand = Brand(
            id="sample-brand",
            name="Sample Brand",
            enabled=True,
            logo=self.logo,
            renderer_profile=RendererProfile(
                accent="#F0C36B", text="#FFFFFF", overlay="#111827"
            ),
            channels=("telegram", "instagram"),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_image_led_card_is_exactly_four_by_five_and_preserves_source(self) -> None:
        output = self.root / "card.png"

        metrics = render_card(
            background=self.background,
            output=output,
            brand=self.brand,
            eyebrow="VIJAYADASHAMI · 20 OCTOBER 2026",
            greeting="May every tool become an instrument of better work.",
            tagline="Wishing you a thoughtful Dussehra.",
        )

        with Image.open(output) as image:
            self.assertEqual(image.size, (1080, 1350))
        self.assertEqual(metrics["width"], 1080)
        self.assertEqual(metrics["height"], 1350)
        self.assertGreater(metrics["image_visible_ratio"], 0.55)

    def test_renderer_rejects_copy_that_would_turn_artwork_into_a_text_panel(self) -> None:
        with self.assertRaisesRegex(RenderError, "greeting"):
            render_card(
                background=self.background,
                output=self.root / "bad.png",
                brand=self.brand,
                eyebrow="FESTIVAL",
                greeting="word " * 40,
                tagline="Short close.",
            )

    def test_renderer_never_overwrites_the_generated_background(self) -> None:
        before = self.background.read_bytes()

        render_card(
            background=self.background,
            output=self.root / "card.png",
            brand=self.brand,
            eyebrow="FESTIVAL",
            greeting="Better beginnings.",
            tagline="With warm wishes.",
        )

        self.assertEqual(self.background.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
