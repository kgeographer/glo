# GLO Package Reference

*Last updated: 2026-02-08*

## Package: `glo/`

Local Python package for place-based color palette extraction.

---

### `glo/io.py` — Image Loading and File I/O

| Function | Signature | Description |
|----------|-----------|-------------|
| `find_photos` | `(place_dir: Path) -> list[Path]` | Find all photo files (.jpg, .jpeg, .png, .tif, .tiff, .heic) in a place directory. Returns sorted list. |
| `load_image` | `(path: Path, max_dim: int = 800) -> Image` | Load image as RGB, downsized so longest side <= max_dim. |
| `save_palette_image` | `(centers, counts, out_path, width=1200, height=150) -> Path` | Save a proportional palette strip as PNG/JPEG. |

---

### `glo/colors.py` — Color Space Conversions

| Function | Signature | Description |
|----------|-----------|-------------|
| `rgb_image_to_lab_array` | `(image: Image) -> ndarray` | Convert PIL RGB image to flat LAB pixel array [H*W, 3]. |
| `lab_array_to_rgb_colors` | `(lab_centers: ndarray) -> ndarray` | Convert LAB cluster centers to RGB uint8 [n, 3]. |
| `image_to_pixels` | `(image, sample_fraction=0.2, random_state=42) -> ndarray` | Convert image to sampled RGB float32 array [n_samples, 3]. |

---

### `glo/extract.py` — Palette Extraction Algorithms

| Function | Signature | Description |
|----------|-----------|-------------|
| `extract_palette_kmeans` | `(image, n_colors=6, sample_fraction=0.2, color_space="lab", random_state=42)` | K-means palette from a single image. Returns (centers_rgb, counts). |
| `sample_lab_pixels_from_images` | `(image_paths, pixels_per_image=5000, max_dim=800, random_state=42) -> ndarray` | Pool equal LAB pixel samples from multiple images. |
| `kmeans_palette_from_lab_pixels` | `(lab_pixels, n_colors=8, random_state=42)` | K-means on pre-sampled LAB pixels. Returns (centers_rgb, counts). |
| `extract_accent_palette` | `(lab_pixels, n_colors=4, chroma_percentile=85.0, random_state=42)` | Palette from highest-chroma pixels only. Returns (centers_rgb, counts). |

---

### `glo/visualize.py` — Visualization and Layouts

| Function | Signature | Description |
|----------|-----------|-------------|
| `render_palette_strip` | `(centers, counts, width=400, height=80) -> Image` | Render a single proportional palette strip as PIL Image. |
| `render_composite` | `(place_palettes, cols=5, strip_width=400, strip_height=80, ...)  -> Image` | Render a labeled grid of palette strips. Each entry in `place_palettes` is a dict with keys: `name`, `centers`, `counts`. |

---

## Scripts: `scripts/`

### `scripts/extract_palette.py` — Per-Place Palette Extraction

Extracts palettes from one or more place directories. Outputs a palette strip PNG, optional accent strip PNG, and a JSON sidecar with RGB values and proportions.

```bash
# Single place
python scripts/extract_palette.py santafe

# Multiple places with accent palettes
python scripts/extract_palette.py santafe abiqui shiprock --n-colors 10 --accent

# All places (excluding Albania)
python scripts/extract_palette.py --all --exclude albania --n-colors 6
```

| Flag | Default | Description |
|------|---------|-------------|
| `places` | *(positional)* | Place folder names |
| `--all` | false | Process all directories in `data/images/` |
| `--exclude` | [] | Places to skip when using `--all` |
| `--n-colors` | 8 | Number of palette colors |
| `--pixels-per-image` | 5000 | LAB pixels sampled per image |
| `--max-dim` | 800 | Max image dimension for loading |
| `--accent` | false | Also extract high-chroma accent palette |
| `--accent-colors` | 4 | Number of accent colors |
| `--chroma-percentile` | 85.0 | Chroma threshold for accent extraction |
| `--output-dir` | `output/palettes` | Output directory |

**Outputs per place:** `{place}_palette.png`, `{place}_palette.json`, optionally `{place}_accent.png`

### `scripts/roadtrip_composite.py` — Multi-Place Composite Grid

Generates a labeled grid image of palette strips for a sequence of places. Place order in the argument list determines display order.

```bash
# Southwest road trip, 2 rows of 5
python scripts/roadtrip_composite.py \
    santafe abiqui shiprock tubacity windowrock \
    seligman grandcanyon redrock deathvalley eastbay \
    --cols 5 --output output/palettes/southwest_roadtrip.png

# Accent palette version
python scripts/roadtrip_composite.py \
    santafe abiqui shiprock tubacity windowrock \
    seligman grandcanyon redrock deathvalley eastbay \
    --cols 5 --accent --accent-colors 5
```

| Flag | Default | Description |
|------|---------|-------------|
| `places` | *(positional, required)* | Place folder names in display order |
| `--cols` | 5 | Columns in grid |
| `--strip-width` | 400 | Palette strip width (px) |
| `--strip-height` | 80 | Palette strip height (px) |
| `--n-colors` | 8 | Colors per palette |
| `--accent` | false | Use high-chroma accent palettes |
| `--accent-colors` | 5 | Number of accent colors |
| `--chroma-percentile` | 85.0 | Chroma threshold for accent |
| `--pixels-per-image` | 5000 | LAB pixels per image |
| `--max-dim` | 800 | Max image dimension |
| `--output` | `output/palettes/composite.png` | Output image path |

**Outputs:** composite PNG + JSON summary. Compound folder names (e.g., `grandcanyon`) are automatically mapped to display names (e.g., "Grand Canyon").

---

## Data Layout

```
data/images/{place}/        # Photos directly in place folder
                            # e.g., data/images/santafe/santafe_01.jpg
output/palettes/            # Generated palette images and data
```

## Dependencies

numpy, Pillow, scikit-learn, matplotlib, scikit-image
