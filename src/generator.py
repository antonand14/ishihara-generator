"""
Ishihara plate generator core logic.
Generates a circle-packed image where circles spelling out text
are colored differently from background circles.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import math


PLATE_SIZE = 600
PLATE_RADIUS = 280
MIN_R = 2
MAX_R = 6


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _vary_color(base_rgb: tuple, variance: int = 25) -> tuple:
    return tuple(
        max(0, min(255, c + random.randint(-variance, variance)))
        for c in base_rgb
    )


def _render_text_mask(text: str, size: int) -> np.ndarray:
    """Returns a binary mask (size x size) where text pixels are True."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    font_size = max(40, size // max(len(text), 1) + 10)
    font = None
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (IOError, OSError):
            continue

    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Scale font to fit within ~60% of plate diameter
    target = int(size * 0.55)
    if tw > 0:
        font_size = int(font_size * target / tw)
        font_size = max(20, min(font_size, size // 2))
        try:
            font = font.font_variant(size=font_size) if hasattr(font, "font_variant") else ImageFont.truetype(font.path, font_size)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), text, fill=255, font=font)

    return np.array(img) > 128


def _pack_circles(text_mask: np.ndarray, cx: int, cy: int, min_r: int = MIN_R, max_r: int = MAX_R):
    """
    Random placement with spatial hash for fast overlap checks.
    Tries random positions; accepts if no overlap with already-placed circles.
    """
    size = text_mask.shape[0]
    placed = []          # (x, y, r)
    cell = max_r * 2     # spatial hash cell size

    grid = {}  # (col, row) -> list of indices into placed

    def grid_cells(x, y, r):
        """All grid cells a circle with centre x,y radius r touches."""
        for gx in range((x - r) // cell, (x + r) // cell + 1):
            for gy in range((y - r) // cell, (y + r) // cell + 1):
                yield gx, gy

    def overlaps(x, y, r):
        for key in grid_cells(x, y, r):
            for idx in grid.get(key, []):
                px, py, pr = placed[idx]
                if math.hypot(x - px, y - py) < r + pr:
                    return True
        return False

    def add(x, y, r):
        idx = len(placed)
        placed.append((x, y, r))
        for key in grid_cells(x, y, r):
            grid.setdefault(key, []).append(idx)

    attempts = 0
    max_attempts = 200000
    while attempts < max_attempts:
        attempts += 1
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, PLATE_RADIUS)
        x = int(cx + dist * math.cos(angle))
        y = int(cy + dist * math.sin(angle))
        r = random.randint(min_r, max_r)

        if math.hypot(x - cx, y - cy) + r > PLATE_RADIUS:
            continue
        if overlaps(x, y, r):
            continue

        add(x, y, r)

    circles = []
    for x, y, r in placed:
        nx = max(0, min(x, size - 1))
        ny = max(0, min(y, size - 1))
        circles.append((x, y, r, bool(text_mask[ny, nx])))
    return circles


def generate_plate(text: str, fg_color: str, bg_color: str, min_r: int = MIN_R, max_r: int = MAX_R) -> Image.Image:
    """
    Generate an Ishihara-style plate image.
    fg_color: color for circles that form the text
    bg_color: color for background circles
    """
    fg_rgb = _hex_to_rgb(fg_color)
    bg_rgb = _hex_to_rgb(bg_color)

    img = Image.new("RGB", (PLATE_SIZE, PLATE_SIZE), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    cx, cy = PLATE_SIZE // 2, PLATE_SIZE // 2

    # Draw plate boundary circle (light gray background)
    draw.ellipse(
        [cx - PLATE_RADIUS, cy - PLATE_RADIUS, cx + PLATE_RADIUS, cy + PLATE_RADIUS],
        fill=(220, 220, 220),
        outline=(180, 180, 180),
        width=2,
    )

    text_mask = _render_text_mask(text, PLATE_SIZE)
    circles = _pack_circles(text_mask, cx, cy, min_r, max_r)

    for x, y, r, is_text in circles:
        color = _vary_color(fg_rgb if is_text else bg_rgb)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    return img
