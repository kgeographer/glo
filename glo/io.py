"""Image loading and palette file I/O."""

from pathlib import Path

import numpy as np
from PIL import Image

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic"}


def find_photos(place_dir: Path) -> list[Path]:
    """Return sorted list of photo files in a place directory."""
    photos = sorted(
        p for p in place_dir.iterdir() if p.suffix.lower() in PHOTO_EXTS
    )
    return photos


def load_image(path: Path, max_dim: int = 800) -> Image.Image:
    """Load an image as RGB, downsized so longest side <= max_dim."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dim / max(w, h))
    if scale < 1.0:
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
    return img


def save_palette_image(
    centers: np.ndarray,
    counts: np.ndarray,
    out_path: Path,
    width: int = 1200,
    height: int = 150,
) -> Path:
    """Save a horizontal palette strip as PNG/JPEG. Returns the output path."""
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

    # Fill any remaining pixels with the last color (rounding)
    if current_x < width:
        img[:, current_x:, :] = centers[-1]

    pil_img = Image.fromarray(img)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pil_img.save(out_path)
    return out_path
