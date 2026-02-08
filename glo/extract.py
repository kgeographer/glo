"""Palette extraction algorithms."""

from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

from .colors import (
    image_to_pixels,
    lab_array_to_rgb_colors,
    rgb_image_to_lab_array,
)
from .io import load_image


def extract_palette_kmeans(
    image,
    n_colors: int = 6,
    sample_fraction: float = 0.2,
    color_space: str = "lab",
    random_state: int = 42,
):
    """
    Cluster image pixels into n_colors via k-means.

    Returns:
        centers_rgb: [n_colors, 3] uint8
        counts:      [n_colors] pixel counts per cluster
    """
    if color_space.lower() == "rgb":
        pixels = image_to_pixels(image, sample_fraction=sample_fraction, random_state=random_state)
    elif color_space.lower() == "lab":
        lab_pixels = rgb_image_to_lab_array(image)
        if 0 < sample_fraction < 1.0:
            rng = np.random.default_rng(random_state)
            n = lab_pixels.shape[0]
            idx = rng.choice(n, size=int(n * sample_fraction), replace=False)
            lab_pixels = lab_pixels[idx]
        pixels = lab_pixels
    else:
        raise ValueError(f"Unsupported color_space: {color_space}")

    kmeans = KMeans(n_clusters=n_colors, random_state=random_state, n_init="auto")
    labels = kmeans.fit_predict(pixels)
    centers = kmeans.cluster_centers_
    counts = np.bincount(labels, minlength=n_colors)

    if color_space.lower() == "rgb":
        centers_rgb = np.clip(centers, 0, 255).astype(np.uint8)
    else:
        centers_rgb = lab_array_to_rgb_colors(centers)

    sort_idx = np.argsort(counts)[::-1]
    return centers_rgb[sort_idx], counts[sort_idx]


def sample_lab_pixels_from_images(
    image_paths: list[Path],
    pixels_per_image: int = 5000,
    max_dim: int = 800,
    random_state: int = 42,
) -> np.ndarray:
    """
    Load multiple images, convert to LAB, sample equal pixel counts.
    Returns stacked array [total_samples, 3].
    """
    rng = np.random.default_rng(random_state)
    all_samples = []

    for path in image_paths:
        img = load_image(path, max_dim=max_dim)
        lab = rgb_image_to_lab_array(img)
        n_pixels = lab.shape[0]
        n_sample = min(pixels_per_image, n_pixels)
        idx = rng.choice(n_pixels, size=n_sample, replace=False)
        all_samples.append(lab[idx])

    return np.vstack(all_samples)


def kmeans_palette_from_lab_pixels(
    lab_pixels: np.ndarray,
    n_colors: int = 8,
    random_state: int = 42,
):
    """
    K-means on pre-sampled LAB pixels.

    Returns:
        centers_rgb: [n_colors, 3] uint8
        counts:      [n_colors]
    """
    kmeans = KMeans(n_clusters=n_colors, random_state=random_state, n_init="auto")
    labels = kmeans.fit_predict(lab_pixels)
    centers_lab = kmeans.cluster_centers_
    counts = np.bincount(labels, minlength=n_colors)

    sort_idx = np.argsort(counts)[::-1]
    centers_rgb = lab_array_to_rgb_colors(centers_lab[sort_idx])
    return centers_rgb, counts[sort_idx]


def extract_accent_palette(
    lab_pixels: np.ndarray,
    n_colors: int = 4,
    chroma_percentile: float = 85.0,
    random_state: int = 42,
):
    """
    Palette from only the highest-chroma (most saturated) pixels.

    Returns:
        centers_rgb: [n_colors, 3] uint8
        counts:      [n_colors]
    """
    a = lab_pixels[:, 1]
    b = lab_pixels[:, 2]
    chroma = np.sqrt(a * a + b * b)

    threshold = np.percentile(chroma, chroma_percentile)
    high_chroma = lab_pixels[chroma >= threshold]

    if high_chroma.shape[0] < n_colors:
        raise ValueError(
            f"Only {high_chroma.shape[0]} high-chroma pixels found; "
            f"need at least {n_colors}. Lower chroma_percentile."
        )

    return kmeans_palette_from_lab_pixels(high_chroma, n_colors=n_colors, random_state=random_state)
