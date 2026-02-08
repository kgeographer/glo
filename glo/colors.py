"""Color space conversions and utilities."""

import numpy as np
from PIL import Image
from skimage import color


def rgb_image_to_lab_array(image: Image.Image) -> np.ndarray:
    """Convert a PIL RGB image to a flat LAB pixel array [H*W, 3]."""
    rgb = np.array(image) / 255.0
    lab = color.rgb2lab(rgb)  # (H, W, 3)
    h, w, c = lab.shape
    return lab.reshape(-1, c).astype(np.float32)


def lab_array_to_rgb_colors(lab_centers: np.ndarray) -> np.ndarray:
    """Convert LAB cluster centers to RGB [0-255] uint8."""
    lab_img = lab_centers.reshape(1, -1, 3)
    rgb = color.lab2rgb(lab_img)  # 0-1 floats
    rgb = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    return rgb.reshape(-1, 3)


def image_to_pixels(
    image: Image.Image,
    sample_fraction: float = 0.2,
    random_state: int = 42,
) -> np.ndarray:
    """Convert image to [n_samples, 3] RGB float32 array with optional subsampling."""
    rng = np.random.default_rng(random_state)
    arr = np.array(image)
    h, w, c = arr.shape
    pixels = arr.reshape(-1, c)

    if 0 < sample_fraction < 1.0:
        n_pixels = pixels.shape[0]
        n_sample = int(n_pixels * sample_fraction)
        idx = rng.choice(n_pixels, size=n_sample, replace=False)
        pixels = pixels[idx]

    return pixels.astype(np.float32)
