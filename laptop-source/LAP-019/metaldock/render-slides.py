from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw, ImageFont
from pathlib import Path
import glob
import json
import math
import os
import subprocess
import zipfile


# ============================================================================
# DAILY PAYLOAD
# Everything that may change from one brief to the next lives here.
# ============================================================================

BRIEF = {
    "brief_date_iso": "2026-09-09",
    "brief_date_display": "Wednesday, 9 September 2026",
    "brief_date_badge": "9 SEP 2026",
    "session_date_display": "Tuesday, 8 September 2026",

    "cover_headline": "Nickel bounces, but NPI buying stays cautious",
    "cover_thesis": "India remains firmer than global NPI signals.",

    "active_sections": [
        "GLOBAL MARKETS",
        "INDIA DOMESTIC",
        "POLICY UPDATES",
        "MARKET OUTLOOK",
    ],

    "cover_sources": [
        "Sources: SMM, BigMint and DGTR, 7–9 Sep 2026.",
        "Session sources: SMM LME page, SMM NPI analysis and DGTR notice.",
    ],

    "slides": [
        {
            "eyebrow": "GLOBAL MARKETS",
            "accent": "Core inputs mixed",
            "headline": "Nickel bounced, but NPI buying stayed cautious",
            "cards": [
                {
                    "label": "SHFE stainless close",
                    "value": "7 Sep: RMB 13,885/mt",
                    "body": "Up RMB 30 from 4 Sep and down RMB 5 from 31 Aug; SMM said demand stayed need-based.",
                },
                {
                    "label": "LME 3M nickel",
                    "value": "8 Sep: USD 16,755/mt",
                    "body": "Up USD 65 from the previous close of USD 16,690.",
                },
                {
                    "label": "China high-grade NPI",
                    "value": "7 Sep: CNY 1,100.5/mtu",
                    "body": "8–12% daily ex-works assessment, down CNY 4 from the previous Friday.",
                },
            ],
            "read_label": "INPUT READ",
            "read_through": (
                "Nickel bounced for the session, while NPI pricing and "
                "stainless demand still point to cautious raw-material buying."
            ),
            "sources": [
                "Sources: SMM stainless daily review, 7 Sep 2026; SMM LME page, 8 Sep session.",
                "Sources: SMM NPI analysis, 7 Sep 2026.",
            ],
        },
        {
            "eyebrow": "GLOBAL MARKETS",
            "accent": "Inventory caps buying",
            "headline": "Higher port stocks keep mills patient",
            "cards": [
                {
                    "label": "Indonesia NPI FOB",
                    "value": "7 Sep: USD 142.7/mtu",
                    "body": "Down USD 0.7 from the previous Friday.",
                },
                {
                    "label": "300-series social inventory",
                    "value": "3 Sep: 581.9 kt",
                    "body": "Down 6 kt week-on-week; still above early-August levels.",
                },
                {
                    "label": "High-grade NPI port stock",
                    "value": "3 Sep: 35.3 kt Ni",
                    "body": "+59.7% from 22.1 kt Ni on 13 Aug.",
                },
            ],
            "read_label": "INVENTORY READ",
            "read_through": (
                "Port material has rebuilt, while mills with ample raw-material "
                "stocks are pausing procurement and waiting on prices."
            ),
            "sources": [
                "Sources: SMM NPI analysis, 7 Sep 2026; SMM Nickel Flash, 8 Sep 2026.",
                "Sources: SMM stainless daily review, 7 Sep 2026.",
            ],
        },
        {
            "eyebrow": "INDIA DOMESTIC",
            "accent": "India stays firmer",
            "headline": "Domestic signals resist full pass-through",
            "cards": [
                {
                    "label": "Bright-bar exports",
                    "value": "Firm WoW",
                    "body": (
                        "BigMint said Indian stainless bright-bar export prices "
                        "remained firm week-on-week despite weak demand."
                    ),
                },
                {
                    "label": "Stainless scrap",
                    "value": "Inched up WoW",
                    "body": (
                        "BigMint said stainless scrap prices inched up "
                        "week-on-week amid supply shortage."
                    ),
                },
                {
                    "label": "India H1 output",
                    "value": "2.16 million t",
                    "body": "Up from 2.05 million t; +5.4% year-on-year.",
                },
            ],
            "read_label": "INDIA READ",
            "read_through": (
                "Indian stainless signals are firmer than the global NPI tone, "
                "so local pass-through can lag raw-material easing."
            ),
            "sources": [
                "Sources: BigMint stainless insights, 8 Sep 2026 and 4 Sep 2026.",
                "Sources: BigMint global stainless production report, 8 Sep 2026.",
            ],
        },
        {
            "eyebrow": "POLICY UPDATES",
            "accent": "Hearing is two days away",
            "headline": "Policy timing is the near-term shock risk",
            "cards": [
                {
                    "label": "DGTR oral hearing",
                    "value": "11 Sep, 3:30 PM IST",
                    "body": (
                        "Cold-rolled stainless 300/400-series case from "
                        "China PR, Indonesia and Vietnam."
                    ),
                },
                {
                    "label": "Case status",
                    "value": "Oral hearing latest",
                    "body": (
                        "DGTR case page lists Oral Hearing as the latest timeline "
                        "item and shows no preliminary or final determination."
                    ),
                },
                {
                    "label": "2–4 week read",
                    "value": "Soft-to-flat",
                    "body": (
                        "NPI demand stays weak, but Indian stainless indicators "
                        "are firm; easing looks gradual rather than a reset."
                    ),
                },
            ],
            "read_label": "STEP-CHANGE RISK",
            "read_through": (
                "A new applicable duty outcome in the DGTR cold-rolled "
                "300/400-series case would override the gradual raw-material path."
            ),
            "sources": [
                "Sources: DGTR case page and DGTR home notice, current 9 Sep 2026.",
                "Sources: SMM NPI analysis, 7 Sep 2026; BigMint stainless insights, 8 Sep 2026.",
            ],
        },
    ],
}


# ============================================================================
# STATIC RENDERER CONFIGURATION
# Nothing below BRIEF contains day-specific market content.
# ============================================================================

W = 1080
H = 1350
SAFE_BOTTOM = 1278

BG = (248, 250, 252)
WHITE = (255, 255, 255)
DARK = (15, 23, 42)
PRIMARY = (2, 6, 23)
MUTED = (100, 116, 139)
BORDER = (226, 232, 240)
ACCENT = (37, 99, 235)
DEEP = (29, 78, 216)
BLUE_LIGHT = (147, 197, 253)

LEFT = 72
RIGHT = 1008
CONTENT_W = RIGHT - LEFT

HERO_TOP = 500
HERO_BOTTOM = 1150
DIVIDER_Y = 1158

MIN_SPACING = 24
MAX_SPACING = 160
MIN_CARD_CLEARANCE = 12
MIN_PAGE_CLEARANCE = 8
MIN_TITLE_HERO_CLEARANCE = 12

# Where the brand assets are and where the slides go. The default is the
# scheduled task's sandbox, which is why it is a path and not a flag; CI sets
# these instead of the script being told about CI.
ASSET_DIR = Path(os.environ.get("MD_ASSET_DIR", "/mnt/data"))
OUT_ROOT = Path(os.environ.get("MD_OUT_DIR", "/mnt/data"))

ASSETS = {
    "metal_logo": ASSET_DIR / "Metal_Dock_Black_Logo.png",
    "dockfinity_logo": ASSET_DIR / "dockfinity logo.png",
    "hero": ASSET_DIR / "MD Hero.png",
}

EXPECTED_ASSET_DIMENSIONS = {
    "metal_logo": (2048, 205),
    "dockfinity_logo": (1658, 360),
}

GRADE_LINES = (
    "201 | 202 | 304",
    "316 | 410 | 430",
    "HR | CR | CIRCLES",
)

SECTION_ICON_KIND = {
    "GLOBAL MARKETS": "global",
    "INDIA DOMESTIC": "india",
    "POLICY UPDATES": "policy",
    "UTENSILS DEMAND": "utensils",
    "MARKET OUTLOOK": "outlook",
}

PUBLIC_METHOD_WORDS = (
    "recomputed",
    "carried",
    "verified",
    "not publicly verified",
    "searched",
    "fallback",
)


# ============================================================================
# FONT DISCOVERY
# OTF is always searched before TTF.
# ============================================================================

FONT_ROOTS = (
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local/share/fonts",
)

# The typefaces metaldock.co.in loads: Outfit for display, IBM Plex Sans for
# body. Both ship as a single variable file, so a role is a file plus the
# named weight instance to select inside it.
FONT_NAMES = {
    "body_regular": ("IBMPlexSans", "Regular"),
    "body_medium": ("IBMPlexSans", "Medium"),
    "body_semibold": ("IBMPlexSans", "SemiBold"),
    "body_bold": ("IBMPlexSans", "Bold"),
    "display_regular": ("Outfit", "Regular"),
    "display_semibold": ("Outfit", "SemiBold"),
    "display_bold": ("Outfit", "Bold"),
    "display_black": ("Outfit", "Black"),
}

# A variable font is published under a name carrying its axes, and some
# installs flatten that to the plain family name. Both are tried.
FONT_FILES = {
    "Outfit": ("Outfit[wght].ttf", "Outfit.ttf"),
    "IBMPlexSans": ("IBMPlexSans[wdth,wght].ttf", "IBMPlexSans.ttf"),
}


def find_font_file(family: str) -> Path:
    searched = []

    for filename in FONT_FILES[family]:
        # Checked as a plain path before any globbing. A variable font's
        # filename carries its axes in square brackets — IBMPlexSans[wdth,wght]
        # — and to a glob those brackets are a character class matching one
        # letter, so the file is there and the pattern never finds it.
        for root in FONT_ROOTS:
            direct = root / filename
            searched.append(str(direct))
            if direct.is_file():
                return direct

        for root in FONT_ROOTS:
            if not root.exists():
                continue
            matches = sorted(root.rglob(glob.escape(filename)))
            if matches:
                return matches[0]

    raise FileNotFoundError(
        "Required font could not be found."
        + f"\nFamily: {family}"
        + "\nSearched:\n  - "
        + "\n  - ".join(searched)
    )


FONT_PATHS = {
    key: find_font_file(family)
    for key, (family, _weight) in FONT_NAMES.items()
}


def font(size: int, role: str = "body_regular") -> ImageFont.FreeTypeFont:
    if role not in FONT_NAMES:
        raise KeyError(f"Unknown font role: {role}")

    _family, weight = FONT_NAMES[role]
    loaded = ImageFont.truetype(str(FONT_PATHS[role]), size)
    # A variable font opens at Regular. Without this every bold line would
    # render at normal weight, which looks like a design choice rather than
    # a bug and would go unnoticed.
    loaded.set_variation_by_name(weight)
    return loaded


# ============================================================================
# BASIC GEOMETRY / TEXT HELPERS
# ============================================================================

def round_rect(
    draw: ImageDraw.ImageDraw,
    xy,
    radius,
    fill,
    outline=None,
    width=1,
):
    draw.rounded_rectangle(
        xy,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def text_bbox(
    draw: ImageDraw.ImageDraw,
    xy,
    text,
    font_obj,
    anchor=None,
):
    return draw.textbbox(
        xy,
        text,
        font=font_obj,
        anchor=anchor,
    )


def rect_bottom(rect) -> int:
    return int(math.ceil(rect[3]))


def rect_right(rect) -> int:
    return int(math.ceil(rect[2]))


def rect_distance(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    dx = max(
        bx1 - ax2,
        ax1 - bx2,
        0,
    )
    dy = max(
        by1 - ay2,
        ay1 - by2,
        0,
    )

    return math.hypot(dx, dy)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_obj,
    max_width: float,
):
    words = str(text).split()

    if not words:
        return []

    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if (
            not current
            or draw.textlength(candidate, font=font_obj) <= max_width
        ):
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def fit_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    role: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
):
    for size in range(start_size, min_size - 1, -1):
        font_obj = font(size, role)
        lines = wrap_text(
            draw,
            text,
            font_obj,
            max_width,
        )

        if len(lines) <= max_lines:
            return font_obj, lines

    raise ValueError(
        f"Text does not fit within {max_lines} lines at or above "
        f"{min_size}px. Shorten the BRIEF text: {text!r}"
    )


def measure_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines,
    font_obj,
    line_gap: int,
):
    """Where draw_lines would put each line, without putting it there.

    The cover has to know how tall a headline will be before it commits to a
    size, and draw_lines can only tell you by drawing it.
    """
    boxes = []
    current_y = y

    for line in lines:
        box = text_bbox(
            draw,
            (x, current_y),
            line,
            font_obj,
        )
        boxes.append(box)
        current_y += (box[3] - box[1]) + line_gap

    return boxes


def draw_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines,
    font_obj,
    fill,
    line_gap: int,
):
    boxes = []
    current_y = y

    for line in lines:
        draw.text(
            (x, current_y),
            line,
            font=font_obj,
            fill=fill,
        )

        box = text_bbox(
            draw,
            (x, current_y),
            line,
            font_obj,
        )
        boxes.append(box)

        line_height = box[3] - box[1]
        current_y += line_height + line_gap

    return boxes


def crop_paste(
    background: Image.Image,
    source: Image.Image,
    box,
):
    x, y, width, height = box

    src_w, src_h = source.size
    scale = max(
        width / src_w,
        height / src_h,
    )

    resized_w = round(src_w * scale)
    resized_h = round(src_h * scale)

    resized = source.resize(
        (resized_w, resized_h),
        Image.LANCZOS,
    )

    left = (resized_w - width) // 2
    top = (resized_h - height) // 2

    cropped = resized.crop(
        (
            left,
            top,
            left + width,
            top + height,
        )
    ).convert("RGBA")

    background.alpha_composite(
        cropped,
        (x, y),
    )


def letterspace(
    draw: ImageDraw.ImageDraw,
    xy,
    text: str,
    font_obj,
    fill,
    target_width: int,
):
    x, y = xy

    glyph_width = sum(
        draw.textlength(
            char,
            font=font_obj,
        )
        for char in text
    )

    gaps = max(
        1,
        len(text) - 1,
    )

    extra = (
        target_width - glyph_width
    ) / gaps

    cursor_x = x
    boxes = []

    for char in text:
        draw.text(
            (cursor_x, y),
            char,
            font=font_obj,
            fill=fill,
        )

        boxes.append(
            text_bbox(
                draw,
                (cursor_x, y),
                char,
                font_obj,
            )
        )

        cursor_x += (
            draw.textlength(
                char,
                font=font_obj,
            )
            + extra
        )

    return (
        x,
        min(box[1] for box in boxes),
        x + target_width,
        max(box[3] for box in boxes),
    )


def remove_near_white_background(
    image: Image.Image,
) -> Image.Image:
    converted = image.convert("RGBA")
    pixels = converted.load()

    for y in range(converted.height):
        for x in range(converted.width):
            r, g, b, a = pixels[x, y]

            if (
                a > 0
                and r > 245
                and g > 245
                and b > 245
            ):
                pixels[x, y] = (
                    r,
                    g,
                    b,
                    0,
                )

    return converted


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_brief():
    required_root = (
        "brief_date_iso",
        "brief_date_display",
        "brief_date_badge",
        "session_date_display",
        "cover_headline",
        "cover_thesis",
        "active_sections",
        "cover_sources",
        "slides",
    )

    for key in required_root:
        if key not in BRIEF:
            raise KeyError(
                f"BRIEF is missing required key: {key}"
            )

    if not BRIEF["slides"]:
        raise ValueError(
            "BRIEF must contain at least one data slide."
        )

    if len(BRIEF["cover_sources"]) > 2:
        raise ValueError(
            "Cover may carry at most two source lines."
        )

    for section in BRIEF["active_sections"]:
        if section not in SECTION_ICON_KIND:
            raise ValueError(
                f"Unknown active section: {section}"
            )

    headline = BRIEF["cover_headline"].strip()

    if not headline:
        raise ValueError(
            "cover_headline may not be empty."
        )

    if (
        headline.isupper()
        and any(char.isalpha() for char in headline)
    ):
        raise ValueError(
            "cover_headline must be sentence case, not all caps."
        )

    for index, slide in enumerate(
        BRIEF["slides"],
        start=1,
    ):
        required_slide = (
            "eyebrow",
            "accent",
            "headline",
            "cards",
            "read_label",
            "read_through",
            "sources",
        )

        for key in required_slide:
            if key not in slide:
                raise KeyError(
                    f"Data slide {index} is missing key: {key}"
                )

        if len(slide["cards"]) > 3:
            raise ValueError(
                f"Data slide {index} has more than three cards."
            )

        if len(slide["sources"]) > 2:
            raise ValueError(
                f"Data slide {index} has more than two source lines."
            )

        for card_index, card in enumerate(
            slide["cards"],
            start=1,
        ):
            for key in (
                "label",
                "value",
                "body",
            ):
                if key not in card:
                    raise KeyError(
                        f"Data slide {index}, card {card_index} "
                        f"is missing key: {key}"
                    )

        public_strings = [
            slide["eyebrow"],
            slide["accent"],
            slide["headline"],
            slide["read_label"],
            slide["read_through"],
            *slide["sources"],
        ]

        for card in slide["cards"]:
            public_strings.extend(
                (
                    card["label"],
                    card["value"],
                    card["body"],
                )
            )

        for value in public_strings:
            lowered = value.lower()

            for forbidden in PUBLIC_METHOD_WORDS:
                if forbidden in lowered:
                    raise ValueError(
                        "Public slide content contains prohibited "
                        f"method language: {forbidden!r}"
                    )


# ============================================================================
# STATIC ASSET VALIDATION
# ============================================================================

def load_assets():
    for name, path in ASSETS.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Required asset is missing: {name}: {path}"
            )

    metal = Image.open(
        ASSETS["metal_logo"]
    ).convert("RGBA")

    dock_raw = Image.open(
        ASSETS["dockfinity_logo"]
    ).convert("RGBA")

    hero = Image.open(
        ASSETS["hero"]
    ).convert("RGB")

    actual = {
        "metal_logo": metal.size,
        "dockfinity_logo": dock_raw.size,
    }

    for name, expected in EXPECTED_ASSET_DIMENSIONS.items():
        if actual[name] != expected:
            raise ValueError(
                f"{name} dimensions are {actual[name]}, "
                f"expected {expected}"
            )

    dock = remove_near_white_background(
        dock_raw
    )

    return metal, dock_raw, dock, hero


# ============================================================================
# ICONS
# ============================================================================

def draw_section_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    kind: str,
    color=WHITE,
):
    if kind == "global":
        radius = 12

        draw.ellipse(
            (
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
            ),
            outline=color,
            width=2,
        )

        draw.line(
            (
                cx - radius,
                cy,
                cx + radius,
                cy,
            ),
            fill=color,
            width=1,
        )

        draw.line(
            (
                cx,
                cy - radius,
                cx,
                cy + radius,
            ),
            fill=color,
            width=1,
        )

        draw.arc(
            (
                cx - 7,
                cy - radius,
                cx + 7,
                cy + radius,
            ),
            0,
            360,
            fill=color,
            width=1,
        )

    elif kind == "india":
        draw.rectangle(
            (
                cx - 12,
                cy - 8,
                cx + 12,
                cy + 10,
            ),
            outline=color,
            width=2,
        )

        draw.line(
            (
                cx - 8,
                cy - 3,
                cx + 8,
                cy + 5,
            ),
            fill=color,
            width=2,
        )

    elif kind == "policy":
        draw.line(
            (
                cx,
                cy - 12,
                cx,
                cy + 12,
            ),
            fill=color,
            width=2,
        )

        draw.line(
            (
                cx - 12,
                cy - 7,
                cx + 12,
                cy - 7,
            ),
            fill=color,
            width=2,
        )

        draw.arc(
            (
                cx - 15,
                cy - 7,
                cx - 5,
                cy + 9,
            ),
            0,
            180,
            fill=color,
            width=2,
        )

        draw.arc(
            (
                cx + 5,
                cy - 7,
                cx + 15,
                cy + 9,
            ),
            0,
            180,
            fill=color,
            width=2,
        )

    elif kind == "utensils":
        draw.ellipse(
            (
                cx - 13,
                cy - 5,
                cx + 13,
                cy + 8,
            ),
            outline=color,
            width=2,
        )

        draw.line(
            (
                cx - 8,
                cy - 9,
                cx + 8,
                cy - 9,
            ),
            fill=color,
            width=2,
        )

        draw.line(
            (
                cx,
                cy - 9,
                cx,
                cy - 13,
            ),
            fill=color,
            width=2,
        )

    elif kind == "outlook":
        draw.line(
            (
                cx - 12,
                cy + 8,
                cx - 2,
                cy - 4,
            ),
            fill=color,
            width=2,
        )

        draw.line(
            (
                cx - 2,
                cy - 4,
                cx + 4,
                cy + 2,
            ),
            fill=color,
            width=2,
        )

        draw.line(
            (
                cx + 4,
                cy + 2,
                cx + 12,
                cy - 10,
            ),
            fill=color,
            width=2,
        )

    else:
        raise ValueError(
            f"Unknown section icon kind: {kind}"
        )


# ============================================================================
# FOOTER
# ============================================================================

def draw_footer(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    page_number: int,
    total_pages: int,
    source_lines,
    session_date: str,
    dock_logo: Image.Image,
):
    draw.line(
        (
            LEFT,
            DIVIDER_Y,
            RIGHT,
            DIVIDER_Y,
        ),
        fill=BORDER,
        width=2,
    )

    source_font = font(
        16,
        "body_regular",
    )

    source_boxes = []
    source_y = 1172

    for source in source_lines[:2]:
        draw.text(
            (
                LEFT,
                source_y,
            ),
            source,
            font=source_font,
            fill=MUTED,
        )

        box = text_bbox(
            draw,
            (
                LEFT,
                source_y,
            ),
            source,
            source_font,
        )

        source_boxes.append(box)
        source_y += 20

    session_font = font(
        16,
        "body_semibold",
    )

    session_text = (
        "Session used: "
        + session_date
    )

    session_xy = (
        LEFT,
        1218,
    )

    draw.text(
        session_xy,
        session_text,
        font=session_font,
        fill=MUTED,
    )

    session_box = text_bbox(
        draw,
        session_xy,
        session_text,
        session_font,
    )

    page_font = font(
        17,
        "body_semibold",
    )

    page_text = (
        f"{page_number}/{total_pages}"
    )

    page_xy = (
        LEFT,
        1254,
    )

    draw.text(
        page_xy,
        page_text,
        font=page_font,
        fill=MUTED,
    )

    page_box = text_bbox(
        draw,
        page_xy,
        page_text,
        page_font,
    )

    managed_font = font(
        15,
        "body_regular",
    )

    managed_text = "Managed by"
    managed_xy = (
        760,
        1241,
    )

    draw.text(
        managed_xy,
        managed_text,
        font=managed_font,
        fill=MUTED,
    )

    managed_box = text_bbox(
        draw,
        managed_xy,
        managed_text,
        managed_font,
    )

    target_logo_height = 34
    target_logo_width = int(
        dock_logo.width
        * target_logo_height
        / dock_logo.height
    )

    logo = dock_logo.resize(
        (
            target_logo_width,
            target_logo_height,
        ),
        Image.LANCZOS,
    )

    logo_xy = (
        RIGHT - target_logo_width,
        1234,
    )

    image.alpha_composite(
        logo,
        logo_xy,
    )

    logo_box = (
        logo_xy[0],
        logo_xy[1],
        logo_xy[0] + target_logo_width,
        logo_xy[1] + target_logo_height,
    )

    other_boxes = [
        *source_boxes,
        session_box,
        managed_box,
        logo_box,
    ]

    page_clearance = min(
        rect_distance(
            page_box,
            other_box,
        )
        for other_box in other_boxes
    )

    if page_clearance < MIN_PAGE_CLEARANCE:
        raise RuntimeError(
            "Page number is too close to another footer element: "
            f"{page_clearance:.1f}px"
        )

    footer_boxes = [
        *source_boxes,
        session_box,
        page_box,
        managed_box,
        logo_box,
    ]

    return {
        "boxes": footer_boxes,
        "page_clearance": page_clearance,
        "max_bottom": max(
            rect_bottom(box)
            for box in footer_boxes
        ),
    }


# ============================================================================
# COVER
# ============================================================================

def render_cover(
    metal_logo: Image.Image,
    dock_logo: Image.Image,
    hero: Image.Image,
    total_pages: int,
):
    image = Image.new(
        "RGBA",
        (W, H),
        BG + (255,),
    )

    draw = ImageDraw.Draw(
        image
    )

    rendered_boxes = []

    # Masthead
    draw.rectangle(
        (
            0,
            0,
            W,
            210,
        ),
        fill=BG,
    )

    logo_width = 620
    logo_height = int(
        metal_logo.height
        * logo_width
        / metal_logo.width
    )

    resized_logo = metal_logo.resize(
        (
            logo_width,
            logo_height,
        ),
        Image.LANCZOS,
    )

    logo_xy = (
        LEFT,
        44,
    )

    image.alpha_composite(
        resized_logo,
        logo_xy,
    )

    rendered_boxes.append(
        (
            logo_xy[0],
            logo_xy[1],
            logo_xy[0] + logo_width,
            logo_xy[1] + logo_height,
        )
    )

    tagline_box = letterspace(
        draw,
        (
            LEFT,
            122,
        ),
        "STAINLESS STEEL SUPPLY",
        font(
            25,
            "body_semibold",
        ),
        MUTED,
        logo_width,
    )

    rendered_boxes.append(
        tagline_box
    )

    draw.line(
        (
            812,
            48,
            812,
            166,
        ),
        fill=BORDER,
        width=2,
    )

    grade_size = 22

    while grade_size >= 12:
        grade_font = font(
            grade_size,
            "display_bold",
        )

        grade_boxes = []

        for index, grade_line in enumerate(
            GRADE_LINES
        ):
            xy = (
                842,
                55 + index * 36,
            )

            grade_boxes.append(
                text_bbox(
                    draw,
                    xy,
                    grade_line,
                    grade_font,
                )
            )

        if max(
            rect_right(box)
            for box in grade_boxes
        ) <= RIGHT:
            break

        grade_size -= 1

    if grade_size < 12:
        raise RuntimeError(
            "Grade block cannot fit inside the right safe margin."
        )

    for index, grade_line in enumerate(
        GRADE_LINES
    ):
        xy = (
            842,
            55 + index * 36,
        )

        draw.text(
            xy,
            grade_line,
            font=grade_font,
            fill=(
                ACCENT
                if index == len(GRADE_LINES) - 1
                else PRIMARY
            ),
        )

        rendered_boxes.append(
            text_bbox(
                draw,
                xy,
                grade_line,
                grade_font,
            )
        )

    # Title band
    draw.rectangle(
        (
            0,
            210,
            W,
            HERO_TOP,
        ),
        fill=BG,
    )

    masthead_font = font(
        25,
        "display_black",
    )

    masthead_xy = (
        LEFT,
        250,
    )

    masthead_text = (
        "STAINLESS STEEL RAW-MATERIAL INTELLIGENCE"
    )

    draw.text(
        masthead_xy,
        masthead_text,
        font=masthead_font,
        fill=PRIMARY,
    )

    rendered_boxes.append(
        text_bbox(
            draw,
            masthead_xy,
            masthead_text,
            masthead_font,
        )
    )

    badge_box = (
        748,
        248,
        RIGHT,
        326,
    )

    draw.rectangle(
        badge_box,
        fill=DEEP,
    )

    rendered_boxes.append(
        badge_box
    )

    badge_label_font = font(
        18,
        "body_semibold",
    )

    badge_date_font = font(
        28,
        "display_black",
    )

    badge_label_xy = (
        878,
        268,
    )

    badge_date_xy = (
        878,
        295,
    )

    draw.text(
        badge_label_xy,
        "MARKET BRIEF",
        font=badge_label_font,
        fill=WHITE,
        anchor="ma",
    )

    draw.text(
        badge_date_xy,
        BRIEF["brief_date_badge"],
        font=badge_date_font,
        fill=WHITE,
        anchor="ma",
    )

    rendered_boxes.extend(
        (
            text_bbox(
                draw,
                badge_label_xy,
                "MARKET BRIEF",
                badge_label_font,
                anchor="ma",
            ),
            text_bbox(
                draw,
                badge_date_xy,
                BRIEF["brief_date_badge"],
                badge_date_font,
                anchor="ma",
            ),
        )
    )

    draw.rectangle(
        (
            LEFT,
            354,
            340,
            362,
        ),
        fill=ACCENT,
    )

    # The cover headline has to satisfy two things at once: the two-line
    # limit, and leaving the hero room to breathe. Fitting only the line limit
    # - which is what this did - cannot work. A two-line headline at 42px
    # leaves about -3px of clearance whatever the words are, and the fitter
    # returned the first size that fit two lines, so it never reached 40px,
    # where the same headline fits on one line and clears by 36.
    #
    # The effect was that any brief whose title wrapped was refused, and the
    # refusal blamed the wording. On 18 and 19 September 2026 several attempts
    # were spent rewording a headline that was never the problem.
    headline_font = None
    headline_lines = None

    for candidate_size in range(42, 31, -1):
        candidate_font = font(
            candidate_size,
            "display_black",
        )
        candidate_lines = wrap_text(
            draw,
            BRIEF["cover_headline"],
            candidate_font,
            CONTENT_W,
        )

        if len(candidate_lines) > 2:
            continue

        probe_boxes = measure_lines(
            draw,
            LEFT,
            382,
            candidate_lines,
            candidate_font,
            4,
        )
        probe_thesis = text_bbox(
            draw,
            (
                LEFT,
                max(rect_bottom(b) for b in probe_boxes) + 10,
            ),
            BRIEF["cover_thesis"],
            font(20, "body_regular"),
        )

        if (
            HERO_TOP - rect_bottom(probe_thesis)
            >= MIN_TITLE_HERO_CLEARANCE
        ):
            headline_font = candidate_font
            headline_lines = candidate_lines
            break

    if headline_font is None:
        raise RuntimeError(
            "Cover title band is too deep even at 32px. "
            "Shorten BRIEF['cover_headline'] or BRIEF['cover_thesis']."
        )

    headline_boxes = draw_lines(
        draw=draw,
        x=LEFT,
        y=382,
        lines=headline_lines,
        font_obj=headline_font,
        fill=PRIMARY,
        line_gap=4,
    )

    rendered_boxes.extend(
        headline_boxes
    )

    headline_bottom = max(
        rect_bottom(box)
        for box in headline_boxes
    )

    thesis_font = font(
        20,
        "body_regular",
    )

    if (
        draw.textlength(
            BRIEF["cover_thesis"],
            font=thesis_font,
        )
        > CONTENT_W
    ):
        raise RuntimeError(
            "cover_thesis is too long for one line. "
            "Shorten BRIEF['cover_thesis']."
        )

    thesis_y = (
        headline_bottom + 10
    )

    thesis_xy = (
        LEFT,
        thesis_y,
    )

    thesis_box = text_bbox(
        draw,
        thesis_xy,
        BRIEF["cover_thesis"],
        thesis_font,
    )

    title_hero_clearance = (
        HERO_TOP
        - rect_bottom(thesis_box)
    )

    if (
        title_hero_clearance
        < MIN_TITLE_HERO_CLEARANCE
    ):
        raise RuntimeError(
            "Cover title band is too deep. "
            "Shorten BRIEF['cover_thesis'] or BRIEF['cover_headline']. "
            f"Measured clearance: {title_hero_clearance}px"
        )

    draw.text(
        thesis_xy,
        BRIEF["cover_thesis"],
        font=thesis_font,
        fill=MUTED,
    )

    rendered_boxes.append(
        thesis_box
    )

    # Hero
    crop_paste(
        image,
        hero.convert("RGBA"),
        (
            0,
            HERO_TOP,
            W,
            HERO_BOTTOM - HERO_TOP,
        ),
    )

    rendered_boxes.append(
        (
            0,
            HERO_TOP,
            W,
            HERO_BOTTOM,
        )
    )

    # Active section row only
    row_top = 1040
    row_bottom = HERO_BOTTOM

    draw.rectangle(
        (
            0,
            row_top,
            W,
            row_bottom,
        ),
        fill=DARK,
    )

    active_sections = (
        BRIEF["active_sections"]
    )

    if not active_sections:
        raise ValueError(
            "At least one active cover section is required."
        )

    cell_width = (
        W / len(active_sections)
    )

    section_font = font(
        18,
        "body_bold",
    )

    for index, section_name in enumerate(
        active_sections
    ):
        center_x = int(
            index * cell_width
            + cell_width / 2
        )

        draw_section_icon(
            draw,
            center_x,
            1071,
            SECTION_ICON_KIND[section_name],
        )

        section_xy = (
            center_x,
            1110,
        )

        draw.text(
            section_xy,
            section_name,
            font=section_font,
            fill=WHITE,
            anchor="ma",
        )

        rendered_boxes.append(
            text_bbox(
                draw,
                section_xy,
                section_name,
                section_font,
                anchor="ma",
            )
        )

        if index > 0:
            separator_x = int(
                index * cell_width
            )

            draw.line(
                (
                    separator_x,
                    1054,
                    separator_x,
                    1136,
                ),
                fill=WHITE,
                width=1,
            )

    footer_metrics = draw_footer(
        image=image,
        draw=draw,
        page_number=1,
        total_pages=total_pages,
        source_lines=BRIEF["cover_sources"],
        session_date=BRIEF["session_date_display"],
        dock_logo=dock_logo,
    )

    rendered_boxes.extend(
        footer_metrics["boxes"]
    )

    # Real cover clearance is derived from the rendered thesis bbox.
    cover_clearance = (
        HERO_TOP
        - rect_bottom(thesis_box)
    )

    max_content_bottom = max(
        rect_bottom(box)
        for box in rendered_boxes
    )

    if max_content_bottom > SAFE_BOTTOM:
        raise RuntimeError(
            "Cover content exceeds safe area: "
            f"bottom={max_content_bottom}, limit={SAFE_BOTTOM}"
        )

    return image, {
        "tightest_clearance_px": float(
            cover_clearance
        ),
        "title_to_hero_clearance_px": float(
            title_hero_clearance
        ),
        "spacing_px": None,
        "gap_above_divider_px": None,
        "page_clearance_px": float(
            footer_metrics["page_clearance"]
        ),
    }


# ============================================================================
# DATA CARD / PANEL MEASUREMENT
# ============================================================================

def _translate_box(box, x: int, y: int):
    return (
        box[0] + x,
        box[1] + y,
        box[2] + x,
        box[3] + y,
    )


def _compute_card_layout(
    draw: ImageDraw.ImageDraw,
    width: int,
    card,
    label_size=21,
    value_size=39,
    body_size=23,
):
    """Compute the complete card layout once in card-local coordinates.

    Every y position is derived from the actual bbox of the preceding rendered
    element. The resulting relative positions, bboxes, height and clearance are
    the single source of truth used by both measurement and drawing.
    """
    padding = 22
    body_leading = 7

    label_font = font(
        label_size,
        "body_bold",
    )

    value_font = font(
        value_size,
        "display_black",
    )

    body_font = font(
        body_size,
        "body_regular",
    )

    body_lines = wrap_text(
        draw,
        card["body"],
        body_font,
        width - 2 * padding,
    )

    if not body_lines:
        raise ValueError(
            "Card body may not be empty."
        )

    label_text = card["label"].upper()
    label_xy = (
        padding,
        padding,
    )
    label_box = text_bbox(
        draw,
        label_xy,
        label_text,
        label_font,
    )

    value_xy = (
        padding,
        rect_bottom(label_box) + 9,
    )
    value_box = text_bbox(
        draw,
        value_xy,
        card["value"],
        value_font,
    )

    next_body_y = rect_bottom(value_box) + 16
    body_positions = []
    body_boxes = []

    for line in body_lines:
        line_xy = (
            padding,
            next_body_y,
        )
        line_box = text_bbox(
            draw,
            line_xy,
            line,
            body_font,
        )
        body_positions.append(line_xy)
        body_boxes.append(line_box)
        next_body_y = rect_bottom(line_box) + body_leading

    text_bottom = rect_bottom(body_boxes[-1])
    height = int(math.ceil(text_bottom + padding))
    border_box = (
        0,
        0,
        width,
        height,
    )
    clearance = height - text_bottom

    return {
        "height": height,
        "border_box": border_box,
        "clearance": float(clearance),
        "label_text": label_text,
        "label_xy": label_xy,
        "label_box": label_box,
        "value_xy": value_xy,
        "value_box": value_box,
        "body_lines": body_lines,
        "body_positions": body_positions,
        "body_boxes": body_boxes,
        "label_font": label_font,
        "value_font": value_font,
        "body_font": body_font,
        "padding": padding,
        "body_leading": body_leading,
    }


def measure_card(
    draw: ImageDraw.ImageDraw,
    width: int,
    card,
    label_size=21,
    value_size=39,
    body_size=23,
):
    return _compute_card_layout(
        draw,
        width,
        card,
        label_size=label_size,
        value_size=value_size,
        body_size=body_size,
    )


def draw_card(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    card,
    layout=None,
):
    if layout is None:
        layout = measure_card(
            draw,
            width,
            card,
        )

    if layout["border_box"][2] != width:
        raise ValueError(
            "Card layout width does not match draw width."
        )

    border_box = _translate_box(
        layout["border_box"],
        x,
        y,
    )

    round_rect(
        draw,
        border_box,
        22,
        WHITE,
        BORDER,
        2,
    )

    label_xy = (
        x + layout["label_xy"][0],
        y + layout["label_xy"][1],
    )
    draw.text(
        label_xy,
        layout["label_text"],
        font=layout["label_font"],
        fill=MUTED,
    )

    value_xy = (
        x + layout["value_xy"][0],
        y + layout["value_xy"][1],
    )
    draw.text(
        value_xy,
        card["value"],
        font=layout["value_font"],
        fill=PRIMARY,
    )

    for line, line_xy in zip(
        layout["body_lines"],
        layout["body_positions"],
    ):
        draw.text(
            (
                x + line_xy[0],
                y + line_xy[1],
            ),
            line,
            font=layout["body_font"],
            fill=DARK,
        )

    clearance = layout["clearance"]

    if clearance < MIN_CARD_CLEARANCE:
        raise RuntimeError(
            "Card text is too close to the bottom border: "
            f"{clearance:g}px"
        )

    text_boxes = [
        _translate_box(layout["label_box"], x, y),
        _translate_box(layout["value_box"], x, y),
        *[
            _translate_box(box, x, y)
            for box in layout["body_boxes"]
        ],
    ]

    return {
        "box": border_box,
        "height": layout["height"],
        "clearance": float(clearance),
        "text_boxes": text_boxes,
    }


def _compute_panel_layout(
    draw: ImageDraw.ImageDraw,
    width: int,
    label: str,
    body: str,
):
    """Compute one reusable panel layout in panel-local coordinates."""
    padding = 22
    leading = 7

    label_font = font(
        21,
        "body_bold",
    )

    body_font = font(
        23,
        "body_regular",
    )

    body_lines = wrap_text(
        draw,
        body,
        body_font,
        width - 2 * padding,
    )

    if not body_lines:
        raise ValueError(
            "Read-through body may not be empty."
        )

    label_text = label.upper()
    label_xy = (
        padding,
        padding,
    )
    label_box = text_bbox(
        draw,
        label_xy,
        label_text,
        label_font,
    )

    next_body_y = rect_bottom(label_box) + 12
    body_positions = []
    body_boxes = []

    for line in body_lines:
        line_xy = (
            padding,
            next_body_y,
        )
        line_box = text_bbox(
            draw,
            line_xy,
            line,
            body_font,
        )
        body_positions.append(line_xy)
        body_boxes.append(line_box)
        next_body_y = rect_bottom(line_box) + leading

    text_bottom = rect_bottom(body_boxes[-1])
    height = int(math.ceil(text_bottom + padding))
    border_box = (
        0,
        0,
        width,
        height,
    )
    clearance = height - text_bottom

    return {
        "height": height,
        "border_box": border_box,
        "clearance": float(clearance),
        "label_text": label_text,
        "label_xy": label_xy,
        "label_box": label_box,
        "body_lines": body_lines,
        "body_positions": body_positions,
        "body_boxes": body_boxes,
        "label_font": label_font,
        "body_font": body_font,
        "padding": padding,
        "leading": leading,
    }


def measure_panel(
    draw: ImageDraw.ImageDraw,
    width: int,
    label: str,
    body: str,
):
    return _compute_panel_layout(
        draw,
        width,
        label,
        body,
    )


def draw_panel(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    label: str,
    body: str,
    layout=None,
):
    if layout is None:
        layout = measure_panel(
            draw,
            width,
            label,
            body,
        )

    if layout["border_box"][2] != width:
        raise ValueError(
            "Panel layout width does not match draw width."
        )

    border_box = _translate_box(
        layout["border_box"],
        x,
        y,
    )

    round_rect(
        draw,
        border_box,
        22,
        DARK,
        None,
        0,
    )

    label_xy = (
        x + layout["label_xy"][0],
        y + layout["label_xy"][1],
    )
    draw.text(
        label_xy,
        layout["label_text"],
        font=layout["label_font"],
        fill=BLUE_LIGHT,
    )

    for line, line_xy in zip(
        layout["body_lines"],
        layout["body_positions"],
    ):
        draw.text(
            (
                x + line_xy[0],
                y + line_xy[1],
            ),
            line,
            font=layout["body_font"],
            fill=WHITE,
        )

    clearance = layout["clearance"]

    if clearance < MIN_CARD_CLEARANCE:
        raise RuntimeError(
            "Read-through panel text is too close to the "
            f"bottom border: {clearance:g}px"
        )

    text_boxes = [
        _translate_box(layout["label_box"], x, y),
        *[
            _translate_box(box, x, y)
            for box in layout["body_boxes"]
        ],
    ]

    return {
        "box": border_box,
        "height": layout["height"],
        "clearance": float(clearance),
        "text_boxes": text_boxes,
    }


# ============================================================================
# DATA SLIDES
# ============================================================================

def render_data_slide(
    slide_data,
    page_number: int,
    total_pages: int,
    metal_logo: Image.Image,
    dock_logo: Image.Image,
):
    image = Image.new(
        "RGBA",
        (W, H),
        BG + (255,),
    )

    draw = ImageDraw.Draw(
        image
    )

    rendered_boxes = []

    # Masthead mark
    logo_width = 280
    logo_height = int(
        metal_logo.height
        * logo_width
        / metal_logo.width
    )

    resized_logo = metal_logo.resize(
        (
            logo_width,
            logo_height,
        ),
        Image.LANCZOS,
    )

    logo_xy = (
        LEFT,
        44,
    )

    image.alpha_composite(
        resized_logo,
        logo_xy,
    )

    rendered_boxes.append(
        (
            logo_xy[0],
            logo_xy[1],
            logo_xy[0] + logo_width,
            logo_xy[1] + logo_height,
        )
    )

    eyebrow_font = font(
        20,
        "body_bold",
    )

    eyebrow_xy = (
        LEFT,
        136,
    )

    eyebrow_text = (
        slide_data["eyebrow"].upper()
    )

    draw.text(
        eyebrow_xy,
        eyebrow_text,
        font=eyebrow_font,
        fill=MUTED,
    )

    rendered_boxes.append(
        text_bbox(
            draw,
            eyebrow_xy,
            eyebrow_text,
            eyebrow_font,
        )
    )

    accent_font = font(
        30,
        "display_bold",
    )

    accent_xy = (
        LEFT,
        170,
    )

    draw.text(
        accent_xy,
        slide_data["accent"],
        font=accent_font,
        fill=ACCENT,
    )

    rendered_boxes.append(
        text_bbox(
            draw,
            accent_xy,
            slide_data["accent"],
            accent_font,
        )
    )

    headline_font, headline_lines = fit_wrapped_text(
        draw=draw,
        text=slide_data["headline"],
        role="display_black",
        max_width=CONTENT_W,
        max_lines=2,
        start_size=39,
        min_size=34,
    )

    headline_boxes = draw_lines(
        draw=draw,
        x=LEFT,
        y=222,
        lines=headline_lines,
        font_obj=headline_font,
        fill=PRIMARY,
        line_gap=4,
    )

    rendered_boxes.extend(
        headline_boxes
    )

    content_top = (
        max(
            rect_bottom(box)
            for box in headline_boxes
        )
        + 24
    )

    measurement_canvas = (
        Image.new(
            "RGBA",
            (W, H),
            BG + (255,),
        )
    )

    measurement_draw = (
        ImageDraw.Draw(
            measurement_canvas
        )
    )

    card_layouts = [
        measure_card(
            measurement_draw,
            CONTENT_W,
            card,
        )
        for card in slide_data["cards"]
    ]

    panel_measurement = measure_panel(
        measurement_draw,
        CONTENT_W,
        slide_data["read_label"],
        slide_data["read_through"],
    )

    block_heights = [
        layout["height"]
        for layout in card_layouts
    ]
    block_heights.append(
        panel_measurement["height"]
    )

    available = (
        DIVIDER_Y
        - content_top
    )

    content_height = sum(
        block_heights
    )

    gap_count = (
        len(block_heights) + 1
    )

    ideal_spacing = (
        available - content_height
    ) / gap_count

    if ideal_spacing < MIN_SPACING:
        raise RuntimeError(
            f"Slide {page_number} is overfull. "
            f"Computed spacing is {ideal_spacing:.1f}px, "
            f"below minimum {MIN_SPACING}px. "
            "Remove the least-important card from BRIEF."
        )

    if ideal_spacing > MAX_SPACING:
        raise RuntimeError(
            f"Slide {page_number} is underfilled. "
            f"Computed spacing is {ideal_spacing:.1f}px, "
            f"above maximum {MAX_SPACING}px. "
            "Merge content with another slide."
        )

    blocks = []

    cursor_y = (
        content_top
        + ideal_spacing
    )

    for card, card_layout in zip(
        slide_data["cards"],
        card_layouts,
    ):
        block_y = int(
            round(cursor_y)
        )

        rendered = draw_card(
            draw,
            LEFT,
            block_y,
            CONTENT_W,
            card,
            layout=card_layout,
        )

        blocks.append(
            rendered
        )

        rendered_boxes.extend(
            rendered["text_boxes"]
        )

        cursor_y += (
            rendered["height"]
            + ideal_spacing
        )

    panel_y = int(
        round(cursor_y)
    )

    panel = draw_panel(
        draw,
        LEFT,
        panel_y,
        CONTENT_W,
        slide_data["read_label"],
        slide_data["read_through"],
        layout=panel_measurement,
    )

    blocks.append(
        panel
    )

    rendered_boxes.extend(
        panel["text_boxes"]
    )

    # Measure actual rendered geometry, not just the arithmetic target.
    actual_gaps = []

    first_gap = (
        blocks[0]["box"][1]
        - content_top
    )

    actual_gaps.append(
        float(first_gap)
    )

    for previous, current in zip(
        blocks,
        blocks[1:],
    ):
        actual_gaps.append(
            float(
                current["box"][1]
                - previous["box"][3]
            )
        )

    gap_above_divider = float(
        DIVIDER_Y
        - blocks[-1]["box"][3]
    )

    actual_gaps.append(
        gap_above_divider
    )

    if min(actual_gaps) < MIN_SPACING:
        raise RuntimeError(
            f"Slide {page_number} rendered with a gap "
            f"below {MIN_SPACING}px: {actual_gaps}"
        )

    if max(actual_gaps) > MAX_SPACING:
        raise RuntimeError(
            f"Slide {page_number} rendered with a gap "
            f"above {MAX_SPACING}px: {actual_gaps}"
        )

    if (
        max(actual_gaps)
        - min(actual_gaps)
        > 4
    ):
        raise RuntimeError(
            f"Slide {page_number} gap distribution exceeds "
            f"the 4px tolerance: {actual_gaps}"
        )

    measured_spacing = (
        sum(actual_gaps[:-1])
        / len(actual_gaps[:-1])
    )

    tightest_clearance = min(
        block["clearance"]
        for block in blocks
    )

    if (
        tightest_clearance
        < MIN_CARD_CLEARANCE
    ):
        raise RuntimeError(
            f"Slide {page_number} tightest clearance is "
            f"{tightest_clearance:.1f}px."
        )

    footer_metrics = draw_footer(
        image=image,
        draw=draw,
        page_number=page_number,
        total_pages=total_pages,
        source_lines=slide_data["sources"],
        session_date=BRIEF["session_date_display"],
        dock_logo=dock_logo,
    )

    rendered_boxes.extend(
        footer_metrics["boxes"]
    )

    max_content_bottom = max(
        rect_bottom(box)
        for box in rendered_boxes
    )

    if max_content_bottom > SAFE_BOTTOM:
        raise RuntimeError(
            f"Slide {page_number} content exceeds safe area: "
            f"bottom={max_content_bottom}, limit={SAFE_BOTTOM}"
        )

    return image, {
        "tightest_clearance_px": float(
            tightest_clearance
        ),
        "spacing_px": round(
            measured_spacing,
            1,
        ),
        "gap_above_divider_px": round(
            gap_above_divider,
            1,
        ),
        "all_gaps_px": [
            round(value, 1)
            for value in actual_gaps
        ],
        "page_clearance_px": round(
            footer_metrics["page_clearance"],
            1,
        ),
    }


# ============================================================================
# FINAL PNG SAFE-AREA ASSERTION
# This checks the actual saved PNG pixels below the safe boundary.
# ============================================================================

def assert_png_safe_area(
    png_path: Path,
):
    rendered = Image.open(
        png_path
    ).convert("RGB")

    if rendered.size != (W, H):
        raise RuntimeError(
            f"{png_path.name} has dimensions {rendered.size}; "
            f"expected {(W, H)}"
        )

    unsafe_region = rendered.crop(
        (
            0,
            SAFE_BOTTOM + 1,
            W,
            H,
        )
    )

    background = Image.new(
        "RGB",
        unsafe_region.size,
        BG,
    )

    difference = ImageChops.difference(
        unsafe_region,
        background,
    )

    if difference.getbbox() is not None:
        raise RuntimeError(
            f"{png_path.name} contains rendered content "
            f"below y={SAFE_BOTTOM}."
        )


# ============================================================================
# OUTPUT
# ============================================================================

def output_directory() -> Path:
    return OUT_ROOT / (
        "metal_dock_"
        + BRIEF["brief_date_iso"].replace(
            "-",
            "_",
        )
    )


def write_pngs(
    images,
    output_dir: Path,
):
    slides_dir = (
        output_dir / "slides"
    )

    slides_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = []

    for index, image in enumerate(
        images,
        start=1,
    ):
        path = (
            slides_dir
            / f"slide-{index}.png"
        )

        image.convert("RGB").save(
            path,
            format="PNG",
        )

        assert_png_safe_area(
            path
        )

        paths.append(
            path
        )

    return paths


def write_zip(
    slide_paths,
    output_dir: Path,
):
    zip_path = (
        output_dir
        / (
            "Metal-Dock-"
            + BRIEF["brief_date_iso"]
            + "-slides.zip"
        )
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in slide_paths:
            archive.write(
                path,
                arcname=path.name,
            )

    return zip_path


def write_pptx(
    slide_paths,
    output_dir: Path,
):
    pptx_path = (
        output_dir
        / (
            "Metal-Dock-"
            + BRIEF["brief_date_iso"]
            + "-slides.pptx"
        )
    )

    js_path = (
        output_dir
        / "make_pptx.js"
    )

    slide_array = json.dumps(
        [
            str(path)
            for path in slide_paths
        ]
    )

    js_source = f"""
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.defineLayout({{
  name: "METAL_DOCK_PORTRAIT",
  width: 8,
  height: 10
}});
pptx.layout = "METAL_DOCK_PORTRAIT";
pptx.author = "Metal Dock";

const slides = {slide_array};

for (const path of slides) {{
  const slide = pptx.addSlide();
  slide.background = {{ color: "F8FAFC" }};
  slide.addImage({{
    path,
    x: 0,
    y: 0,
    w: 8,
    h: 10
  }});
}}

pptx.writeFile({{
  fileName: {json.dumps(str(pptx_path))}
}});
"""

    js_path.write_text(
        js_source,
        encoding="utf-8",
    )

    subprocess.run(
        [
            "node",
            str(js_path),
        ],
        check=True,
    )

    return pptx_path


# ============================================================================
# RENDER
# ============================================================================

def render():
    validate_brief()

    (
        metal_logo,
        dock_raw,
        dock_logo,
        hero,
    ) = load_assets()

    output_dir = (
        output_directory()
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    dock_transparent_path = (
        output_dir
        / "dockfinity_transparent.png"
    )

    dock_logo.save(
        dock_transparent_path
    )

    total_pages = (
        1 + len(BRIEF["slides"])
    )

    images = []
    metrics = []

    cover_image, cover_metrics = render_cover(
        metal_logo=metal_logo,
        dock_logo=dock_logo,
        hero=hero,
        total_pages=total_pages,
    )

    images.append(
        cover_image
    )

    metrics.append(
        {
            "slide": 1,
            **cover_metrics,
        }
    )

    for page_number, slide_data in enumerate(
        BRIEF["slides"],
        start=2,
    ):
        image, slide_metrics = render_data_slide(
            slide_data=slide_data,
            page_number=page_number,
            total_pages=total_pages,
            metal_logo=metal_logo,
            dock_logo=dock_logo,
        )

        images.append(
            image
        )

        metrics.append(
            {
                "slide": page_number,
                **slide_metrics,
            }
        )

    slide_paths = write_pngs(
        images,
        output_dir,
    )

    zip_path = write_zip(
        slide_paths,
        output_dir,
    )

    # The deck is a convenience for whoever posts by hand; the slides and the
    # ZIP are the deliverable. It needs node and pptxgenjs, which the website's
    # build runner has no reason to carry, so a failure here must not throw
    # away five slides that already rendered and passed every check.
    try:
        pptx_path = write_pptx(
            slide_paths,
            output_dir,
        )
    except Exception as exc:  # noqa: BLE001 - reported, never silent
        pptx_path = None
        print(f"PPTX not written ({exc}). The slides and the ZIP are unaffected.")

    manifest = {
        "brief_date": BRIEF["brief_date_iso"],
        "session_date": BRIEF["session_date_display"],
        "fonts": {
            role: str(path)
            for role, path in FONT_PATHS.items()
        },
        "assets": {
            "metal_logo_dimensions": list(
                metal_logo.size
            ),
            "dockfinity_logo_dimensions": list(
                dock_raw.size
            ),
            "hero_dimensions": list(
                hero.size
            ),
        },
        "metrics": metrics,
        "outputs": {
            "slides": [
                str(path)
                for path in slide_paths
            ],
            "zip": str(
                zip_path
            ),
            "pptx": str(pptx_path) if pptx_path else None,
        },
    }

    manifest_path = (
        output_dir
        / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    for metric in metrics:
        slide_number = (
            metric["slide"]
        )

        clearance = (
            metric[
                "tightest_clearance_px"
            ]
        )

        print(
            f"Slide {slide_number}: "
            f"tightest clearance "
            f"{clearance:.1f}px; "
            f"nothing rendered below "
            f"y={SAFE_BOTTOM}."
        )

        if (
            metric["spacing_px"]
            is not None
        ):
            print(
                f"Slide {slide_number}: "
                f"spacing "
                f"{metric['spacing_px']:.1f}px, "
                f"gap above divider "
                f"{metric['gap_above_divider_px']:.1f}px."
            )

    return manifest


if __name__ == "__main__":
    render()
