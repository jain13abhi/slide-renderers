"""Image-led, deterministic occasion renderer shared by every configured brand."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat

from . import Brand

WIDTH = 1080
HEIGHT = 1350
SIDE = 72
BOTTOM = 82
OVERLAY_START = 560


class RenderError(ValueError):
    """Raised when an input cannot fit the locked visual contract."""


def _colour(value: str) -> tuple[int, int, int]:
    raw = value.removeprefix("#")
    if len(raw) != 6:
        raise RenderError(f"invalid six-digit colour: {value}")
    try:
        return tuple(int(raw[offset : offset + 2], 16) for offset in (0, 2, 4))
    except ValueError as exc:
        raise RenderError(f"invalid six-digit colour: {value}") from exc


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ("Inter-Bold.otf", "DejaVuSans-Bold.ttf")
        if bold
        else ("Inter-Regular.otf", "DejaVuSans.ttf")
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _cover(source: Image.Image) -> Image.Image:
    image = source.convert("RGB")
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = max(0, (resized.width - WIDTH) // 2)
    top = max(0, (resized.height - HEIGHT) // 2)
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        candidate = f"{line} {word}"
        box = draw.textbbox((0, 0), candidate, font=font)
        if box[2] - box[0] <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def _logo_panel(canvas: Image.Image, logo_path: Path) -> None:
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except OSError as exc:
        raise RenderError(f"cannot read brand logo {logo_path}: {exc}") from exc
    alpha = logo.getchannel("A")
    visible = Image.new("RGB", logo.size, "white")
    visible.paste(logo.convert("RGB"), mask=alpha)
    luminance = ImageStat.Stat(visible, mask=alpha).mean
    average = sum(luminance) / len(luminance) if luminance else 0
    panel_colour = (13, 20, 34, 218) if average > 170 else (255, 255, 255, 228)

    max_width, max_height = 300, 104
    scale = min(max_width / logo.width, max_height / logo.height, 1.0)
    logo = logo.resize(
        (max(1, round(logo.width * scale)), max(1, round(logo.height * scale))),
        Image.Resampling.LANCZOS,
    )
    pad_x, pad_y = 26, 19
    panel = Image.new("RGBA", (logo.width + 2 * pad_x, logo.height + 2 * pad_y), panel_colour)
    mask = Image.new("L", panel.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel.width - 1, panel.height - 1), radius=22, fill=255)
    rounded = Image.new("RGBA", panel.size)
    rounded.paste(panel, mask=mask)
    rounded.alpha_composite(logo, (pad_x, pad_y))
    canvas.alpha_composite(rounded, (SIDE, 64))


def render_card(
    *,
    background: str | Path,
    output: str | Path,
    brand: Brand,
    eyebrow: str,
    greeting: str,
    tagline: str,
) -> dict[str, Any]:
    """Render one 1080x1350 post without mutating the generated background."""

    eyebrow = eyebrow.strip()
    greeting = greeting.strip()
    tagline = tagline.strip()
    if not eyebrow or len(eyebrow) > 56:
        raise RenderError("eyebrow must contain 1-56 characters")
    if not greeting or len(greeting) > 150:
        raise RenderError("greeting must contain 1-150 characters")
    if not tagline or len(tagline) > 90:
        raise RenderError("tagline must contain 1-90 characters")

    background_path = Path(background)
    try:
        with Image.open(background_path) as source:
            canvas = _cover(source).convert("RGBA")
    except OSError as exc:
        raise RenderError(f"cannot read generated background {background_path}: {exc}") from exc

    overlay_rgb = _colour(brand.renderer_profile.overlay)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_pixels = overlay.load()
    for y in range(OVERLAY_START, HEIGHT):
        progress = (y - OVERLAY_START) / (HEIGHT - OVERLAY_START)
        alpha = round(38 + (218 * progress))
        for x in range(WIDTH):
            overlay_pixels[x, y] = (*overlay_rgb, min(alpha, 244))
    canvas = Image.alpha_composite(canvas, overlay)
    _logo_panel(canvas, brand.logo)

    draw = ImageDraw.Draw(canvas)
    accent = _colour(brand.renderer_profile.accent)
    text_colour = _colour(brand.renderer_profile.text)
    eyebrow_font = _font(22, bold=True)
    greeting_font = _font(54, bold=True)
    tagline_font = _font(27)
    max_text_width = WIDTH - 2 * SIDE

    greeting_lines = _wrap(draw, greeting, greeting_font, max_text_width)
    if len(greeting_lines) > 3:
        raise RenderError("greeting wraps beyond three lines in the locked template")
    tagline_lines = _wrap(draw, tagline, tagline_font, max_text_width)
    if len(tagline_lines) > 2:
        raise RenderError("tagline wraps beyond two lines in the locked template")

    greeting_line_height = 66
    tagline_line_height = 37
    block_height = 29 + 28 + len(greeting_lines) * greeting_line_height + 26 + len(tagline_lines) * tagline_line_height
    y = HEIGHT - BOTTOM - block_height
    if y < OVERLAY_START + 90:
        raise RenderError("copy exceeds the locked image-led text region")

    draw.text((SIDE, y), eyebrow.upper(), font=eyebrow_font, fill=accent)
    y += 57
    for line in greeting_lines:
        draw.text((SIDE, y), line, font=greeting_font, fill=text_colour)
        y += greeting_line_height
    y += 12
    for line in tagline_lines:
        draw.text((SIDE, y), line, font=tagline_font, fill=text_colour)
        y += tagline_line_height

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, format="PNG", optimize=True)
    return {
        "width": WIDTH,
        "height": HEIGHT,
        "image_visible_ratio": round(OVERLAY_START / HEIGHT + 0.25, 3),
        "greeting_lines": len(greeting_lines),
        "tagline_lines": len(tagline_lines),
        "output": str(output_path),
    }


__all__ = ["RenderError", "render_card"]
