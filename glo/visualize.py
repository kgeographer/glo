"""Palette visualization and composite layout generation."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def render_palette_strip(
    centers: np.ndarray,
    counts: np.ndarray,
    width: int = 400,
    height: int = 80,
) -> Image.Image:
    """Render a proportional palette strip as a PIL Image."""
    total = counts.sum()
    proportions = counts / total

    img = np.zeros((height, width, 3), dtype=np.uint8)
    current_x = 0
    for color, prop in zip(centers, proportions):
        w = int(prop * width)
        if w <= 0:
            continue
        img[:, current_x : current_x + w, :] = color
        current_x += w

    if current_x < width:
        img[:, current_x:, :] = centers[-1]

    return Image.fromarray(img)


def render_composite(
    place_palettes: list[dict],
    cols: int = 5,
    strip_width: int = 400,
    strip_height: int = 80,
    label_height: int = 30,
    padding: int = 12,
    bg_color: tuple = (255, 255, 255),
) -> Image.Image:
    """
    Render a grid of labeled palette strips.

    place_palettes: list of dicts with keys 'name', 'centers', 'counts'
    """
    n = len(place_palettes)
    rows = (n + cols - 1) // cols

    cell_w = strip_width + padding
    cell_h = label_height + strip_height + padding
    canvas_w = cols * cell_w + padding
    canvas_h = rows * cell_h + padding

    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(canvas)

    # Try to load a reasonable font; fall back to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i, entry in enumerate(place_palettes):
        row, col = divmod(i, cols)
        x = padding + col * cell_w
        y = padding + row * cell_h

        # Label
        draw.text((x, y), entry["name"], fill=(40, 40, 40), font=font)

        # Palette strip
        strip = render_palette_strip(
            entry["centers"], entry["counts"],
            width=strip_width, height=strip_height,
        )
        canvas.paste(strip, (x, y + label_height))

    return canvas
