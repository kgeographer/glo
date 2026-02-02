# GLO - Geographic Lens on Objects

## Project Overview

GLO is a color palette extraction project for capturing the characteristic colors of places visited during travel. The goal is to derive empirical color palettes from photographs that can inform artistic practice (watercolor, gouache painting) and potentially generate paint mixing formulas.

## Core Concept

Each place has a distinctive color palette shaped by:
- Earth and sky colors
- Architecture and built environment
- Vegetation and natural features
- Cultural/intentional color choices (e.g., Santa Fe's adobe aesthetic)

The project combines algorithmic extraction with artistic perception to capture these place-based palettes.

## Project Structure

```
_glo/
├── data/
│   └── images/               # Source photos (local only, not tracked)
│       ├── albania/photos/
│       └── santafe/photos/
├── output/
│   └── palettes/             # Generated palette strips (tracked)
├── notebooks/
│   └── palette_experiments.ipynb   # Main experimentation notebook
├── scripts/                  # (empty - future Python modules)
└── docs/                     # Project documentation
```

## Current Technical Approach

1. **Color space**: LAB (perceptually uniform) preferred over RGB for clustering
2. **Clustering**: K-means on sampled pixels from multiple images
3. **Accent extraction**: Filter to high-chroma pixels (top 15% by saturation) before clustering
4. **Output**: Palette strip images (PNG) with RGB values and proportions

## Key Functions in Notebook

- `load_image()` - Load and resize photos
- `rgb_image_to_lab_array()` - Convert to LAB color space
- `extract_palette_kmeans()` - Single-image palette extraction
- `sample_lab_pixels_from_images()` - Multi-image sampling for place-level palettes
- `kmeans_palette_from_lab_pixels()` - Cluster combined samples
- `extract_accent_palette()` - High-chroma color extraction
- `plot_palette()` / `save_palette_image()` - Visualization and export

## Dependencies

- numpy, PIL/Pillow, scikit-learn, matplotlib, scikit-image

## Future Directions

See `docs/assessment.md` for detailed analysis. Key opportunities:
- Semantic segmentation (separate sky/earth/architecture palettes)
- Paint pigment mapping (LAB to Munsell to actual pigments)
- Color naming integration
- Cross-place comparison metrics

## Workflow

1. Copy photos from a trip into `data/palettes/{place}/photos/`
2. Set `PROJECT_SLUG` in notebook to the place name
3. Run cells to extract and visualize palettes
4. Export palette strips for reference while painting
