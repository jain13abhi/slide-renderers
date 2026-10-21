from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from occasion.brand_post import BRAND_ASSETS, BrandAssetError, render_brand_post


class BrandPostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.art = self.root / 'art.png'
        Image.new('RGB', (1122, 1402), '#d69546').save(self.art)
        self.assets = Path(__file__).resolve().parents[2] / 'assets'

    def tearDown(self):
        self.temp.cleanup()

    def test_each_logo_is_the_supplied_asset_not_generated_lettering(self):
        for brand in BRAND_ASSETS:
            with self.subTest(brand=brand):
                result = render_brand_post(artwork=self.art, output=self.root / f'{brand}.png',
                                           brand_id=brand, asset_root=self.assets)
                logo_path = self.assets / BRAND_ASSETS[brand]['logo']
                self.assertEqual(hashlib.sha256(logo_path.read_bytes()).hexdigest(), result['logo_sha256'])
                with Image.open(logo_path).convert('RGBA') as logo:
                    flat = Image.new('RGB', logo.size, 'white')
                    flat.paste(logo, mask=logo.getchannel('A'))
                    bounds = ImageChops.difference(flat, Image.new('RGB', flat.size, 'white')).getbbox()
                    expected = flat.crop(bounds).resize(tuple(result['logo_size']), Image.Resampling.LANCZOS)
                with Image.open(result['output']) as card:
                    self.assertEqual(card.size, (1080, 1350))
                    x, y = result['logo_position']
                    actual = card.crop((x, y, x + expected.width, y + expected.height))
                    self.assertIsNone(ImageChops.difference(actual, expected).getbbox())

    def test_inputs_preserved_and_existing_output_not_overwritten(self):
        before = self.art.read_bytes()
        output = self.root / 'card.png'
        render_brand_post(artwork=self.art, output=output, brand_id='metaldock', asset_root=self.assets)
        self.assertEqual(self.art.read_bytes(), before)
        with self.assertRaisesRegex(BrandAssetError, 'exists'):
            render_brand_post(artwork=self.art, output=output, brand_id='metaldock', asset_root=self.assets)

    def test_refuses_unknown_brand_and_modified_logo(self):
        with self.assertRaisesRegex(BrandAssetError, 'Unknown brand'):
            render_brand_post(artwork=self.art, output=self.root / 'bad.png', brand_id='invented', asset_root=self.assets)
        bad_assets = self.root / 'assets'
        target = bad_assets / BRAND_ASSETS['metaldock']['logo']
        target.parent.mkdir(parents=True)
        target.write_bytes(b'not-the-approved-logo')
        with self.assertRaisesRegex(BrandAssetError, 'fingerprint'):
            render_brand_post(artwork=self.art, output=self.root / 'bad.png', brand_id='metaldock', asset_root=bad_assets)


if __name__ == '__main__':
    unittest.main()
