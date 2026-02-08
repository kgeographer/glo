# GLO Project Assessment: Toolkit Refactoring Phase

*February 2026 — beginning of toolkit01 branch*

## Context

Returning to the project after several months. The notebook-based workflow proved the core extraction pipeline works well. Now refactoring into a reusable package and CLI toolbox for processing the US southwest road trip dataset (10 places, ~40 photos) and future trips.

## What's Solid

- **LAB space + k-means** is the right baseline. Perceptually uniform clustering gives colors that actually look different to the eye, unlike RGB which over-represents greens.
- **High-chroma accent extraction** is genuinely useful. Dominant palettes from any landscape tend to converge on "brown + blue sky." Filtering to top-chroma pixels before clustering surfaces the distinctive colors — turquoise trim, red earth, painted doors.
- **Equal per-image sampling** prevents a single large photo from dominating a place palette.

## What's Missing or Worth Considering

### Lightness/Value Separation

Currently clustering on all three LAB channels equally. For painting, you often want the *value structure* separately from *hue/chroma*. A palette sorted or grouped by lightness (L channel) would be more immediately useful for mixing. Consider extracting a "value scale" alongside the chromatic palette.

### Cluster Stability

K-means is sensitive to initialization and k. The code uses a single `random_state`. Running multiple initializations (sklearn's `n_init` parameter) and potentially using silhouette score or elbow method to suggest k would make results more reproducible.

### Median Cut as Alternative

For *artistic* palette extraction (vs. quantization accuracy), median cut often produces more "painterly" groupings because it recursively splits the color space by the axis of greatest range. Worth having as an option alongside k-means.

### Color Naming / Munsell

Mapping to Munsell notation would bridge directly to paint mixing — Munsell is what watercolorists and paint manufacturers use. The `colour-science` Python package has Munsell conversion utilities.

### Paint Mapping

handprint.com has measured LAB values for hundreds of watercolor pigments. A lookup table matching extracted LAB centers to nearest pigments (by Delta-E distance) would give "closest single pigment" immediately. Two-pigment mixing is harder (Kubelka-Munk) but single-pigment matching is straightforward.

## Architecture Decisions

### Package Structure

Chose `glo/` as a local Python package (not installed via pip) with four modules organized by responsibility:

- **io** — file system concerns (finding photos, loading images, saving output)
- **colors** — color space math (RGB/LAB conversion, pixel sampling)
- **extract** — algorithms (k-means, accent extraction)
- **visualize** — rendering (strips, composite grids)

This separation keeps each module focused and testable. The notebook can import from the package for continued experimentation.

### CLI Over Notebook for Production

Scripts with argparse for repeatable, parameterized runs. The notebook remains for exploration and one-off experiments. This avoids the "which cell did I run last" problem.

### No External Config Dependencies

Using argparse rather than click/typer to keep dependencies minimal. No YAML config files — command-line arguments are sufficient for the current parameter space.
