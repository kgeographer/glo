# GLO - Geographic Lens on Objects

## Project Overview

GLO is a color palette extraction project for capturing the characteristic colors of places visited during travel. The goal is to derive empirical color palettes from photographs that can inform artistic practice (watercolor, gouache painting) and potentially generate paint mixing formulas.

## Core Concept

Each place has a distinctive color palette shaped by:
- Earth and sky colors
- Architecture and built environment
- Vegetation and natural features
- Cultural/intentional color choices (e.g., Santa Fe's adobe aesthetic, Tuba City folk art)

The project combines algorithmic extraction with artistic perception to capture these place-based palettes.

## Project Structure

```
_glo/
├── data/
│   └── images/               # Source photos (local only, not tracked)
│       ├── santafe/          # Photos directly in place dirs
│       ├── abiqui/
│       ├── shiprock/
│       ├── tubacity/
│       └── ...               # 11 places currently
├── output/
│   └── palettes/             # Generated palette outputs (tracked)
│       ├── {place}_palette.png/json   # Algorithmic palettes
│       ├── {place}_accent.png         # High-chroma accent palettes
│       └── sw2026/                    # Project-based manual picks
│           ├── {place}_picked.png/json
│           └── strips.png             # Composite comparison strip
├── glo/                      # Python package
│   ├── __init__.py
│   ├── io.py                 # Image loading, photo finding, palette PNG saving
│   ├── extract.py            # LAB sampling, k-means clustering, accent extraction
│   ├── colors.py             # Color space conversions, naming
│   └── visualize.py          # Plotting utilities
├── scripts/
│   ├── extract_palette.py    # CLI for algorithmic palette extraction
│   ├── roadtrip_composite.py # Multi-place composite palette strips
│   ├── color_picker_server.py # Flask server for manual color picking
│   └── static/
│       └── picker.html       # Browser-based eyedropper tool
├── notebooks/
│   └── palette_experiments.ipynb
└── docs/
    ├── assessment_20250201.md
    ├── assessment_20260208.md
    └── package_reference.md
```

## Two Palette Workflows

### 1. Algorithmic (CLI)
```bash
python scripts/extract_palette.py santafe --n-colors 8 --accent
```
- K-means clustering in LAB color space across all photos for a place
- Produces palettes with color proportions (how dominant each color is)
- Good for objective baseline; tends to over-represent sky/dominant areas

### 2. Manual (Color Picker Web App)
```bash
python scripts/color_picker_server.py
# Open http://localhost:5050
```
- Browse place photos in-browser, click to pick colors with eyedropper
- Artist selects the *essential* colors, not just the statistically dominant ones
- Equal-width swatches (proportions left to artistic judgment)
- Saves to project subfolders (e.g., `output/palettes/sw2026/`)
- Same JSON + PNG output format as CLI scripts

### Project Organization
Palettes are organized by project (e.g., `sw2026` for a southwest 2026 trip). A project groups manual picks for related places, with a composite `strips.png` for cross-place comparison.

## Dependencies

- numpy, PIL/Pillow, scikit-learn, matplotlib, scikit-image, flask

## Current Status

- **glo package**: Extracted from notebook into reusable modules
- **CLI extraction**: Working for single/multiple/all places with accent palettes
- **Color picker**: Working browser tool with project subfolder support
- **sw2026 project**: Manual palettes picked for santafe, abiqui, shiprock, tubacity
- **Data**: 11 place directories with photos (not tracked in git)

## Future Directions

See `docs/assessment_20260208.md` for detailed analysis. Key opportunities:
- Semantic segmentation (separate sky/earth/architecture palettes)
- Paint pigment mapping (LAB to Munsell to actual pigments)
- Color naming integration
- Cross-place comparison metrics
- Proportion weighting in the manual picker (drag swatch edges)
