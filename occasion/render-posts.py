#!/usr/bin/env python3
"""
Two occasion posts, one per brand, deliberately unalike.

Both land in the same WhatsApp on the same morning. If they share a layout
they read as one template with two logos dropped in, which is worse than
either of them alone. So the brands do not share a layout here - only the
words and the discipline.

  Metal Dock   architectural. Carving on the left, a light plate on the right
               carrying the words. Structural, cool, squared off. The asking
               leads and the explanation follows.
  Dockfinity   a still life. The words set directly on the photograph, no
               plate at all. Warm, open. The phrase leads and arrives at the
               asking.

The words come from a JSON file, never from the image model. An image model
asked to render a Prakrit phrase returns something almost right, and almost
right is what gets noticed after posting.

    python occasion/render-posts.py post.json --assets . --out cards \
        --md-background md.png --df-background df.png
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
FONT_ROOTS = [Path.home() / ".fonts", Path("/usr/share/fonts"), Path.cwd()]


class PostError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# The spec. Checked before a pixel is drawn, because the failure this guards
# against is a post that renders cleanly with a field quietly missing.
# --------------------------------------------------------------------------

BRAND_FIELDS = {
    # Deliberately different. The two brands do not say the same sentences in
    # the same order; if they did there would be no reason to draw them twice.
    "metaldock": {"headline", "reading"},
    "dockfinity": {"reading", "ask", "to"},
}


def validate(spec: dict) -> dict:
    def fail(what):
        raise PostError(f"post spec: {what}")

    for key in ("slug", "occasion", "brands"):
        if key not in spec:
            fail(f"{key} is missing")
    if not isinstance(spec["slug"], str) or not spec["slug"].strip():
        fail("slug must be a non-empty string - it names the output files")

    occasion = spec["occasion"]
    if not occasion.get("eyebrow"):
        fail("occasion.eyebrow is missing - it is the only label above the headline")

    # A phrase and its gloss suit an occasion built on words someone does not
    # know. Diwali is not one of those. Both are optional; a gloss without a
    # phrase is an error rather than a layout that quietly drops it.
    phrase = occasion.get("phrase") or []
    gloss = occasion.get("gloss") or []
    if gloss and not phrase:
        fail("occasion.gloss is set but occasion.phrase is not - glossing nothing")
    for pair in gloss:
        if len(pair) != 2:
            fail(f"occasion.gloss entry {pair!r} must be [word, meaning]")

    # Not every occasion belongs to both firms. Vishwakarma Puja is a
    # workshop's day and Metal Dock may mark it alone. Whichever brands are
    # present are checked in full; an unknown one is a typo, not a brand.
    unknown = sorted(set(spec["brands"]) - set(BRAND_FIELDS))
    if unknown:
        fail(f"brands has {', '.join(unknown)}, which is not a brand this renders")
    if not spec["brands"]:
        fail("brands is empty - there is nothing to draw")

    for brand in spec["brands"]:
        required = BRAND_FIELDS[brand]
        block = spec["brands"][brand]
        missing = sorted(required - set(block))
        if missing:
            fail(f"brands.{brand} is missing {', '.join(missing)}")
        for field in required:
            if not block[field]:
                fail(f"brands.{brand}.{field} is empty")

    if "metaldock" in spec["brands"]:
        headline = spec["brands"]["metaldock"]["headline"]
        if not isinstance(headline, list) or not all(isinstance(line, str) for line in headline):
            fail("brands.metaldock.headline must be a list of lines")
        if len(headline) > 3:
            fail(f"brands.metaldock.headline has {len(headline)} lines; three is the most the plate holds")

    return spec


# --------------------------------------------------------------------------


def find_font(filename: str) -> Path:
    for root in FONT_ROOTS:
        if (root / filename).is_file():
            return root / filename
    for root in FONT_ROOTS:
        if root.exists():
            # Escaped: IBMPlexSans[wdth,wght].ttf is a glob character class,
            # and an unescaped rglob for it matches nothing at all.
            found = sorted(root.rglob(glob.escape(filename)))
            if found:
                return found[0]
    raise PostError(f"Font not found: {filename}")


def load(filename, weight, size):
    font = ImageFont.truetype(str(find_font(filename)), size)
    if weight:
        # A variable font opens at Regular. Without this every heavy line
        # renders at normal weight and it reads as a design choice.
        font.set_variation_by_name(weight)
    return font


def wrap(text, font, width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if font.getlength(trial) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_lines(lines, filename, weight, start, floor, width):
    """The largest size at which every line clears the column."""
    size = start
    while size > floor:
        font = load(filename, weight, size)
        if all(font.getlength(line) <= width for line in lines):
            return font, size
        size -= 2
    raise PostError(f"{lines!r} will not fit at {floor}px. Shorten it.")


def draw_block(draw, x, y, lines, font, fill, step):
    """Draws the lines and returns the y of the last one."""
    for i, line in enumerate(lines):
        draw.text((x, y + i * step), line, font=font, fill=fill)
    return y + (len(lines) - 1) * step


def cover(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left, top = (resized.width - W) // 2, (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def placed_logo(assets: Path, name: str, width: int) -> Image.Image:
    path = assets / name
    if not path.is_file():
        raise PostError(f"Logo not found: {path}")
    logo = Image.open(path).convert("RGBA")
    return logo.resize((width, max(1, round(logo.height * width / logo.width))), Image.Resampling.LANCZOS)


def luminance(colour) -> float:
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in colour[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg) -> float:
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def mean_colour(image: Image.Image, box):
    small = image.crop(box).convert("RGB").resize((24, 24))
    pixels = list(small.getdata())
    return tuple(sum(p[i] for p in pixels) // len(pixels) for i in range(3))


def check(fg, bg, where: str, floor=4.5):
    ratio = contrast(fg, bg)
    if ratio < floor:
        raise PostError(
            f"{where}: {ratio:.1f}:1 against {bg}, under {floor}:1. "
            f"The background came back too dark - generate a lighter one."
        )
    return ratio


def spaced(text: str) -> str:
    """Letter-spaced with a thin space. A full space opens the label up by
    about 20px and it stops reading as one word."""
    return "".join(c + " " for c in text)


# ---------------------------------------------------------------------------
# Metal Dock - architectural. A light plate squared against the photograph,
# matching the off-white ground its own website is built on.
# ---------------------------------------------------------------------------

def metaldock(spec: dict, assets: Path, background: Path, out: Path) -> Path:
    occasion, copy = spec["occasion"], spec["brands"]["metaldock"]
    image = cover(background)
    plate_x = 470

    # metaldock.co.in is a light site: an off-white ground, white cards, ink
    # text, electric blue for emphasis. A dark plate matched nothing on it,
    # and put a second large blue-black field next to Dockfinity's.
    PLATE = (247, 249, 251)
    INK = (2, 6, 23)
    TEXT = (15, 23, 42)
    MUTED = (100, 116, 139)
    BLUE = (37, 99, 235)

    panel = image.crop((plate_x, 0, W, H)).convert("RGBA")
    panel = Image.alpha_composite(panel, Image.new("RGBA", panel.size, PLATE + (243,)))
    image.paste(panel.convert("RGB"), (plate_x, 0))

    draw = ImageDraw.Draw(image)
    draw.rectangle([(plate_x, 0), (plate_x + 4, H)], fill=BLUE)
    check(INK, mean_colour(image, (plate_x + 20, 100, W - 20, H - 100)), "Metal Dock plate", 7)

    x = plate_x + 52
    inner = W - x - 52

    md_logo = placed_logo(assets, "assets/metaldock/logo-black.png", 230)
    paatra = placed_logo(assets, "assets/metaldock/paatra-logo.png", 155)

    eyebrow = load("IBMPlexSans[wdth,wght].ttf", "SemiBold", 17)
    head, head_size = fit_lines(copy["headline"], "Outfit[wght].ttf", "Bold", 82, 34, inner)
    word = load("Outfit[wght].ttf", "SemiBold", 27)
    mean = load("IBMPlexSans[wdth,wght].ttf", "Regular", 24)
    reading = load("IBMPlexSans[wdth,wght].ttf", "Regular", 25)
    reading_lines = wrap(copy["reading"], reading, inner)

    gloss = occasion.get("gloss") or []
    joined = " ".join(occasion.get("phrase") or [])
    phrase = phrase_size = None

    # Measured, then spaced. A fixed set of gaps left a hole in the middle of
    # the plate that read as an unfinished layout.
    blocks = [
        ("eyebrow", 22, 0.5),
        ("headline", len(copy["headline"]) * (head_size + 10), 0.9),
        ("rule", 1, 0.9),
    ]
    if joined:
        phrase, phrase_size = fit_lines([joined], "Outfit[wght].ttf", "SemiBold", 40, 24, inner)
        blocks.append(("phrase", phrase_size + 12, 0.5))
    if gloss:
        blocks.append(("gloss", len(gloss) * 42, 0.9))
    blocks.append(("reading", len(reading_lines) * 37, 1.1))
    blocks.append(("foot", 28 + md_logo.height + 84 + paatra.height + 60, 0.0))

    top, foot_limit = 150, H - 76
    content = sum(h for _, h, _ in blocks)
    weights = sum(w for _, _, w in blocks)
    slack = (foot_limit - top) - content
    if slack < 0:
        raise PostError(f"The plate is {-slack:.0f}px short for this copy. Shorten it.")
    gap = slack / weights

    y = top
    for name, height, weight in blocks:
        if name == "eyebrow":
            draw.text((x, y), spaced(occasion["eyebrow"]), font=eyebrow, fill=BLUE)
        elif name == "headline":
            # The asking leads here. Dockfinity opens with the phrase and
            # arrives at the request; this states the request first.
            draw_block(draw, x, y, copy["headline"], head, INK, head_size + 10)
        elif name == "rule":
            draw.line([(x, y), (x + 120, y)], fill=BLUE, width=3)
        elif name == "phrase":
            draw.text((x, y), joined, font=phrase, fill=BLUE)
        elif name == "gloss":
            column = max(word.getlength(g[0]) for g in gloss) + 26
            for i, (term, meaning) in enumerate(gloss):
                draw.text((x, y + i * 42), term, font=word, fill=INK)
                draw.text((x + column, y + i * 42 + 4), meaning, font=mean, fill=MUTED)
        elif name == "reading":
            draw_block(draw, x, y, reading_lines, reading, TEXT, 37)
        elif name == "foot":
            draw.line([(x, y), (W - 52, y)], fill=(214, 222, 232), width=1)
            small = load("IBMPlexSans[wdth,wght].ttf", "SemiBold", 18)
            tiny = load("IBMPlexSans[wdth,wght].ttf", "Regular", 16)

            fy = int(y) + 28
            image.paste(md_logo, (x, fy), md_logo)
            draw.text((x, fy + md_logo.height + 12), "Stainless Steel Supply", font=small, fill=BLUE)
            draw.text((x, fy + md_logo.height + 36), "www.metaldock.co.in", font=tiny, fill=MUTED)

            fy += md_logo.height + 84
            image.paste(paatra, (x, fy), paatra)
            draw.text((x, fy + paatra.height + 12), "Premium Utensils", font=small, fill=BLUE)
            draw.text((x, fy + paatra.height + 36), "www.paatracreations.com", font=tiny, fill=MUTED)
        y += height + gap * weight

    out.mkdir(parents=True, exist_ok=True)
    path = out / f"metaldock-{spec['slug']}.png"
    image.save(path)
    print(f"metaldock: plate contrast {contrast(INK, PLATE):.1f}:1, slack {slack:.0f}px distributed")
    return path


# ---------------------------------------------------------------------------
# Dockfinity - a still life. No plate; the words sit on the photograph itself.
# ---------------------------------------------------------------------------

def dockfinity(spec: dict, assets: Path, background: Path, out: Path) -> Path:
    occasion, copy = spec["occasion"], spec["brands"]["dockfinity"]
    image = cover(background)

    INK = (26, 18, 8)
    GOLD = (124, 78, 4)
    SOFT = (86, 70, 48)
    x, inner = 82, W - 164
    FLOOR = 660  # below this the subject of the photograph begins

    # A wash, not a plate. The stone keeps its grain and its shadows; it is
    # lifted just enough that heavy type sits on it cleanly instead of
    # competing with the light falling across it.
    wash = Image.new("RGBA", (W, FLOOR), (255, 252, 246, 0))
    pixels = wash.load()
    for row in range(FLOOR):
        alpha = int(150 * (1 - row / FLOOR) ** 0.7)
        for col in range(W):
            pixels[col, row] = (255, 252, 246, alpha)
    lifted = Image.alpha_composite(image.crop((0, 0, W, FLOOR)).convert("RGBA"), wash)
    image.paste(lifted.convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(image)
    check(INK, mean_colour(image, (x, 96, W - x, 620)), "Dockfinity ground", 7)

    logo = placed_logo(assets, "assets/dockfinity/logo-colour.png", 250)
    image.paste(logo, (x, 78), logo)

    y = 188
    draw.text((x, y), spaced(occasion["eyebrow"]), font=load("Inter-SemiBold.otf", None, 15), fill=GOLD)
    y += 46

    joined = " ".join(occasion.get("phrase") or [])
    if joined:
        phrase, size = fit_lines([joined], "Syne[wght].ttf", "Bold", 66, 34, inner)
        draw.text((x, y), joined, font=phrase, fill=INK)
        y += size + 30

    draw.line([(x, y), (x + 120, y)], fill=GOLD, width=2)
    y += 30

    gloss = occasion.get("gloss") or []
    if gloss:
        word = load("Syne[wght].ttf", "Bold", 26)
        mean = load("Inter-SemiBold.otf", None, 22)
        column = max(word.getlength(g[0]) for g in gloss) + 28
        for i, (term, meaning) in enumerate(gloss):
            draw.text((x, y + i * 36), term, font=word, fill=GOLD)
            draw.text((x + column, y + i * 36 + 3), meaning, font=mean, fill=SOFT)
        y += len(gloss) * 36 + 28

    reading = load("Inter-SemiBold.otf", None, 25)
    y = draw_block(draw, x, y, wrap(copy["reading"], reading, inner), reading, INK, 37) + 54

    ask = load("Inter-SemiBold.otf", None, 24)
    y = draw_block(draw, x, y, wrap(copy["ask"], ask, inner), ask, INK, 36) + 46

    to = load("Inter-Regular.otf", None, 22)
    y = draw_block(draw, x, y, wrap(copy["to"], to, inner), to, SOFT, 33) + 22

    if y > FLOOR:
        raise PostError(f"The copy reaches y={y:.0f}, into the subject of the photograph. Shorten it.")

    # No plate and no strip: one quiet line, on the stone, at the foot.
    draw.line([(x, H - 108), (W - x, H - 108)], fill=(198, 176, 136), width=1)
    draw.text((x, H - 84), "DOCKFINITY", font=load("Syne[wght].ttf", "Bold", 21), fill=INK)
    draw.text((x, H - 56), "Dockware Labs  ·  Trading Dock  ·  Impressio Dock",
              font=load("Inter-SemiBold.otf", None, 17), fill=GOLD)
    draw.text((x, H - 30), "Technology Holding Company  ·  New Delhi  ·  www.dockfinity.com",
              font=load("Inter-Regular.otf", None, 15), fill=SOFT)

    out.mkdir(parents=True, exist_ok=True)
    path = out / f"dockfinity-{spec['slug']}.png"
    image.save(path)
    print(f"dockfinity: copy ends y={y:.0f} of {FLOOR}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path, help="the post JSON")
    parser.add_argument("--assets", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("cards"))
    parser.add_argument("--md-background", type=Path)
    parser.add_argument("--df-background", type=Path)
    args = parser.parse_args()

    spec = validate(json.loads(args.spec.read_text(encoding="utf-8")))
    drawing = {"metaldock": (metaldock, args.md_background),
               "dockfinity": (dockfinity, args.df_background)}
    for brand in spec["brands"]:
        draw_brand, background = drawing[brand]
        if background is None:
            raise PostError(f"brands.{brand} is in the spec but no background was given for it")
        draw_brand(spec, args.assets, background, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
