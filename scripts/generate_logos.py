from __future__ import annotations

import math
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "core/static/core/branding"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 600, 260

COLORS: Dict[str, str] = {
    "emerald": "#1DA97A",
    "lilac": "#C89BFF",
    "violet": "#5E21B6",
    "sky": "#2C7BEA",
    "banana": "#F7C948",
    "mist": "#F2F5F7",
    "trunk": "#8C5A2B",
    "leaf": "#107552",
    "berry": "#E257F4",
}


def _font_candidates() -> List[Path]:
    return [
        Path("/System/Library/Fonts/Supplemental/Arial Rounded MT Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Marker Felt.ttc"),
        Path("/Library/Fonts/Arial Rounded MT Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ]


_font_cache: Dict[int, ImageFont.FreeTypeFont] = {}


def load_font(size: int) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]
    for candidate in _font_candidates():
        if candidate.exists():
            font = ImageFont.truetype(str(candidate), size=size)
            _font_cache[size] = font
            return font
    font = ImageFont.load_default()
    _font_cache[size] = font
    return font


def rounded_rect(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], radius: int, fill: str, outline: str, width: int) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_text(draw: ImageDraw.ImageDraw, position: Tuple[int, int], text: str, size: int, fill: str) -> None:
    font = load_font(size)
    draw.text(position, text, font=font, fill=fill)


def draw_jungle_coin(draw: ImageDraw.ImageDraw) -> None:
    rounded_rect(draw, (20, 20, 580, 240), radius=40, fill=COLORS["mist"], outline=COLORS["trunk"], width=6)
    draw.ellipse((70, 60, 210, 200), fill=COLORS["banana"])
    draw.ellipse((90, 80, 190, 180), outline="#E2A828", width=6)
    draw.ellipse((95, 85, 155, 145), fill="#FFEFA4")
    draw.ellipse((125, 115, 150, 140), fill="#FFEFA4")
    draw.ellipse((90, 35, 150, 95), fill=COLORS["emerald"])
    draw.ellipse((130, 35, 190, 95), fill=COLORS["emerald"])
    draw.rectangle((120, 95, 138, 140), fill=COLORS["emerald"])
    draw.ellipse((105, 125, 125, 145), fill=COLORS["violet"])
    draw.ellipse((155, 125, 175, 145), fill=COLORS["violet"])
    draw.arc((105, 140, 175, 190), start=200, end=340, width=5, fill=COLORS["violet"])
    draw_text(draw, (260, 95), "LEARNING", 52, COLORS["emerald"])
    draw_text(draw, (260, 165), "JUNGLE", 62, COLORS["violet"])
    draw_text(draw, (260, 210), "Jungle Coin Smile", 20, COLORS["trunk"])


def draw_canopy_sign(draw: ImageDraw.ImageDraw) -> None:
    rounded_rect(draw, (15, 25, 585, 235), radius=50, fill="#FFFFFF", outline=COLORS["emerald"], width=6)
    draw.rectangle((60, 40, 120, 200), fill=COLORS["trunk"])
    draw.rounded_rectangle((35, 25, 145, 135), radius=40, fill=COLORS["emerald"])
    draw.ellipse((65, 60, 115, 110), fill="#2BB883")
    draw.line((80, 200, 80, 235), fill=COLORS["trunk"], width=20)
    draw_text(draw, (200, 70), "LEARNING", 58, COLORS["violet"])
    draw_text(draw, (200, 140), "JUNGLE", 64, COLORS["sky"])
    draw_text(draw, (200, 192), "Canopy Signpost", 22, COLORS["trunk"])
    draw.line((200, 125, 520, 125), fill=COLORS["banana"], width=6)
    draw.line((200, 185, 520, 185), fill=COLORS["emerald"], width=3)


def draw_trail_badge(draw: ImageDraw.ImageDraw) -> None:
    rounded_rect(draw, (25, 25, 575, 235), radius=60, fill=COLORS["mist"], outline=COLORS["sky"], width=6)
    draw.ellipse((60, 40, 240, 220), fill=COLORS["sky"])
    draw.ellipse((75, 55, 225, 205), outline="#163C6B", width=5)
    path_points = [(90, 190), (120, 160), (150, 170), (180, 120), (210, 100)]
    draw.line(path_points, fill="#FFFFFF", width=14, joint="curve")
    for x, y in path_points:
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=COLORS["banana"])
    draw.regular_polygon((210, 80, 14), n_sides=5, fill=COLORS["banana"], outline="#E2A828")
    draw_text(draw, (300, 80), "LEARNING", 54, COLORS["emerald"])
    draw_text(draw, (300, 140), "JUNGLE", 64, COLORS["banana"])
    draw_text(draw, (300, 195), "Trail Badge", 24, COLORS["violet"])
    draw.line((300, 170, 540, 170), fill=COLORS["violet"], width=4)


def create_svg(content: str, name: str) -> None:
    (OUTPUT_DIR / f"{name}.svg").write_text(content.strip() + "\n", encoding="utf-8")


def jungle_coin_svg() -> str:
    return f"""
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="560" height="220" rx="40" fill="{COLORS['mist']}" stroke="{COLORS['trunk']}" stroke-width="6"/>
  <circle cx="140" cy="130" r="70" fill="{COLORS['banana']}"/>
  <circle cx="140" cy="130" r="55" fill="none" stroke="#E2A828" stroke-width="6"/>
  <circle cx="125" cy="115" r="25" fill="#FFEFA4"/>
  <circle cx="155" cy="135" r="20" fill="#FFEFA4"/>
  <ellipse cx="120" cy="70" rx="35" ry="30" fill="{COLORS['emerald']}"/>
  <ellipse cx="160" cy="70" rx="35" ry="30" fill="{COLORS['emerald']}"/>
  <rect x="125" y="90" width="26" height="60" fill="{COLORS['emerald']}"/>
  <circle cx="125" cy="135" r="12" fill="{COLORS['violet']}"/>
  <circle cx="165" cy="135" r="12" fill="{COLORS['violet']}"/>
  <path d="M110 160 Q140 190 170 160" stroke="{COLORS['violet']}" stroke-width="5" fill="none"/>
  <text x="260" y="120" font-family="Baloo 2, 'Nunito', sans-serif" font-size="52" fill="{COLORS['emerald']}">LEARNING</text>
  <text x="260" y="190" font-family="Baloo 2, 'Nunito', sans-serif" font-size="62" fill="{COLORS['violet']}">JUNGLE</text>
  <text x="260" y="220" font-family="'Nunito', sans-serif" font-size="20" fill="{COLORS['trunk']}">Jungle Coin Smile</text>
</svg>
"""


def canopy_sign_svg() -> str:
    return f"""
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="15" y="25" width="570" height="210" rx="50" fill="#FFFFFF" stroke="{COLORS['emerald']}" stroke-width="6"/>
  <rect x="60" y="40" width="60" height="160" fill="{COLORS['trunk']}"/>
  <rect x="80" y="200" width="20" height="50" fill="{COLORS['trunk']}"/>
  <rect x="35" y="25" width="110" height="110" rx="40" fill="{COLORS['emerald']}"/>
  <circle cx="90" cy="85" r="25" fill="#2BB883"/>
  <line x1="200" y1="125" x2="520" y2="125" stroke="{COLORS['banana']}" stroke-width="6"/>
  <line x1="200" y1="185" x2="520" y2="185" stroke="{COLORS['emerald']}" stroke-width="3"/>
  <text x="200" y="120" font-family="Baloo 2, 'Nunito', sans-serif" font-size="58" fill="{COLORS['violet']}">LEARNING</text>
  <text x="200" y="185" font-family="Baloo 2, 'Nunito', sans-serif" font-size="64" fill="{COLORS['sky']}">JUNGLE</text>
  <text x="200" y="215" font-family="'Nunito', sans-serif" font-size="22" fill="{COLORS['trunk']}">Canopy Signpost</text>
</svg>
"""


def trail_badge_svg() -> str:
    return f"""
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="25" y="25" width="550" height="210" rx="60" fill="{COLORS['mist']}" stroke="{COLORS['sky']}" stroke-width="6"/>
  <circle cx="150" cy="130" r="90" fill="{COLORS['sky']}"/>
  <circle cx="150" cy="130" r="75" fill="none" stroke="#163C6B" stroke-width="5"/>
  <polyline points="90,190 120,160 150,170 180,120 210,100" fill="none" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="90" cy="190" r="8" fill="{COLORS['banana']}"/>
  <circle cx="120" cy="160" r="8" fill="{COLORS['banana']}"/>
  <circle cx="150" cy="170" r="8" fill="{COLORS['banana']}"/>
  <circle cx="180" cy="120" r="8" fill="{COLORS['banana']}"/>
  <circle cx="210" cy="100" r="8" fill="{COLORS['banana']}"/>
  <polygon points="210,66 218,86 240,86 222,98 228,118 210,106 192,118 198,98 180,86 202,86" fill="{COLORS['banana']}" stroke="#E2A828" stroke-width="2"/>
  <text x="300" y="120" font-family="Baloo 2, 'Nunito', sans-serif" font-size="54" fill="{COLORS['emerald']}">LEARNING</text>
  <text x="300" y="185" font-family="Baloo 2, 'Nunito', sans-serif" font-size="64" fill="{COLORS['banana']}">JUNGLE</text>
  <text x="300" y="215" font-family="'Nunito', sans-serif" font-size="24" fill="{COLORS['violet']}">Trail Badge</text>
  <line x1="300" y1="170" x2="540" y2="170" stroke="{COLORS['violet']}" stroke-width="4"/>
</svg>
"""


IDEAS: List[Tuple[str, Callable[[ImageDraw.ImageDraw], None], Callable[[], str]]] = [
    ("logo-jungle-coin", draw_jungle_coin, jungle_coin_svg),
    ("logo-canopy-sign", draw_canopy_sign, canopy_sign_svg),
    ("logo-trail-badge", draw_trail_badge, trail_badge_svg),
]


def main() -> None:
    for name, drawer, svg_fn in IDEAS:
        img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        drawer(draw)
        img.save(OUTPUT_DIR / f"{name}.png")
        create_svg(svg_fn(), name)
        print(f"Generated {name}.png and {name}.svg")


if __name__ == "__main__":
    main()
