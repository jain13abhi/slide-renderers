"""Compose original brand PNGs without asking an image model to redraw logos.

Standalone creative utility only; does not modify the locked production renderer.
The owner explicitly requires the supplied original logo files, not AI lettering.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

BRAND_ASSETS = {
    'metaldock': {'logo': 'brand-originals/metaldock.png', 'website': 'metaldock.co.in',
                 'colour': '#1F57C3', 'descriptor': 'STAINLESS STEEL SUPPLY',
                 'sha256': '600a2d377df4e3e47d4a29be5148bbe0ffa1e730fead26e33bcb8c3b3b6eef6b'},
    'dockfinity': {'logo': 'brand-originals/dockfinity.png', 'website': 'dockfinity.com',
                  'colour': '#172557', 'descriptor': '',
                  'sha256': 'bc72035a660c5157aae3102397090a1e696016b14c45ee7814e6b4e3b93a9af0'},
    'paatra': {'logo': 'brand-originals/paatra.png', 'website': 'paatracreations.com',
              'colour': '#351C0C', 'descriptor': '',
              'sha256': '345054f92a7995af6d1c5097e5a23977e380e97bdd3fa0ffb12af25a56e767f9'},
}


class BrandAssetError(ValueError):
    pass


def _font(size: int, supplied: str | Path | None):
    for candidate in ([str(supplied)] if supplied else []) + ['Inter-Regular.otf', 'DejaVuSans.ttf']:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def render_brand_post(*, artwork: str | Path, output: str | Path, brand_id: str,
                      asset_root: str | Path, font_path: str | Path | None = None) -> dict:
    if brand_id not in BRAND_ASSETS:
        raise BrandAssetError('Unknown brand; do not invent branding')
    source, destination = Path(artwork), Path(output)
    if destination.exists():
        raise BrandAssetError('Output already exists; choose a versioned filename')
    config = BRAND_ASSETS[brand_id]
    logo_path = Path(asset_root) / config['logo']
    fingerprint = hashlib.sha256(logo_path.read_bytes()).hexdigest()
    if fingerprint != config['sha256']:
        raise BrandAssetError('Original logo fingerprint mismatch; owner review required')
    with Image.open(logo_path).convert('RGBA') as logo:
        flat = Image.new('RGB', logo.size, 'white')
        flat.paste(logo, mask=logo.getchannel('A'))
    bounds = ImageChops.difference(flat, Image.new('RGB', flat.size, 'white')).getbbox()
    if bounds is None:
        raise BrandAssetError('Original logo is blank')
    mark = flat.crop(bounds)
    scale = min(840 / mark.width, 106 / mark.height)
    mark = mark.resize((round(mark.width * scale), round(mark.height * scale)), Image.Resampling.LANCZOS)
    width, height, header, footer = 1080, 1350, 174, 64
    card = Image.new('RGB', (width, height), 'white')
    with Image.open(source) as opened:
        art = opened.convert('RGB')
    art = art.resize((width, round(art.height * width / art.width)), Image.Resampling.LANCZOS)
    body_height = height - header - footer
    if art.height < body_height:
        raise BrandAssetError('Artwork is too short for this portrait composition')
    card.paste(art.crop((0, 0, width, body_height)), (0, header))
    x, y = (width - mark.width) // 2, (header - mark.height - (28 if config['descriptor'] else 0)) // 2
    card.paste(mark, (x, y))
    draw = ImageDraw.Draw(card)
    if config['descriptor']:
        draw.text((width // 2, y + mark.height + 10), config['descriptor'],
                  font=_font(21, font_path), fill='#334155', anchor='mt')
    draw.rectangle((0, header - 5, width - 1, header - 1), fill=config['colour'])
    draw.rectangle((0, height - footer, width - 1, height - 1), fill=config['colour'])
    draw.text((width // 2, height - footer // 2), config['website'],
              font=_font(29, font_path), fill='white', anchor='mm')
    destination.parent.mkdir(parents=True, exist_ok=True)
    card.save(destination, format='PNG', optimize=True)
    return {'output': str(destination), 'brand': brand_id, 'logo_sha256': fingerprint,
            'logo_position': [x, y], 'logo_size': list(mark.size), 'width': width, 'height': height}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artwork', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--brand', choices=tuple(BRAND_ASSETS), required=True)
    parser.add_argument('--asset-root', default=str(Path(__file__).resolve().parents[1] / 'assets'))
    parser.add_argument('--font')
    args = parser.parse_args()
    print(json.dumps(render_brand_post(artwork=args.artwork, output=args.output,
                                      brand_id=args.brand, asset_root=args.asset_root, font_path=args.font)))
