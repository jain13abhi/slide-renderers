"""Fitting-copy layout stability; no providers or pixel inference."""
import unittest
from PIL import ImageFont
from unittest import mock
from occasion.engine import renderer


class VisualContractTests(unittest.TestCase):
    def test_locked_layout_keeps_exact_fonts_and_positions(self):
        font = ImageFont.load_default(size=20)
        with mock.patch.object(renderer, '_font', return_value=font) as load:
            layout = renderer.validate_copy_layout(eyebrow='FESTIVAL', greeting='Warm wishes.', tagline='With care.')
        self.assertEqual(load.call_args_list, [mock.call(22, bold=True), mock.call(54, bold=True), mock.call(27)])
        self.assertEqual(layout['greeting_lines'], ['Warm wishes.'])
        self.assertEqual(layout['tagline_lines'], ['With care.'])
        self.assertEqual(layout['y'], 1082)
