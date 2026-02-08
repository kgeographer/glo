# GLO Project Assessment

*Initial technical review - February 2026*

## What's Working Well

### LAB Color Space
Good choice. LAB is perceptually uniform, so k-means distances correspond better to how we actually see color differences. RGB clustering tends to over-represent certain hues due to the non-uniform nature of that color space.

### High-Chroma Accent Extraction
This is clever. Dominant colors by pixel count often give you "dirt brown and sky blue" - the *distinctive* colors of a place may be less frequent but more salient (the turquoise trim in Santa Fe, for instance). Filtering to the top 15% by chroma before clustering surfaces these accent colors.

### Multi-Image Aggregation
Pooling samples across photos helps capture the *place* rather than a single scene. Equal sampling per image prevents one large photo from dominating.

---

## Opportunities for Enhancement

### Semantic Segmentation

Currently all pixels are treated equally. But the palette of Santa Fe *architecture* differs from Santa Fe *landscape*. Modern segmentation models (SAM, DeepLab) could extract separate palettes for:
- Sky
- Earth/ground
- Vegetation
- Built structures/architecture
- Water

This would enable statements like "the adobe walls cluster around these 3 colors" rather than mixing all scene elements together.

### Alternative to Pure Frequency Weighting

K-means optimizes for cluster compactness, not distinctiveness. Consider:

- **Median cut algorithm** - The classic image quantization approach, often produces more pleasing palettes
- **DBSCAN** - Finds natural clusters without pre-specifying k
- **Hierarchical clustering** - Reveals relationships between colors
- **Sorting by saturation/chroma** rather than frequency for display - the *character* of Santa Fe isn't brown (most frequent) but the warm terracottas and turquoise accents

### Color Naming

Mapping RGB/LAB values to named colors (or Munsell notation) would help bridge to paint mixing. Available resources:
- XKCD color survey data (~1000 named colors with RGB values)
- Munsell renotation data
- Color naming models (there's academic work on this)

A color at LAB(65, 25, 35) could be labeled "terracotta" or "Munsell 5YR 6/6" - more useful for artistic practice than raw numbers.

### Paint Mixing / Pigment Mapping

This is the "long shot" goal but genuinely achievable. The challenge:
- Paint mixing is *subtractive* (unlike light, which is additive)
- It's non-linear (mixing two paints doesn't give you the midpoint)
- Pigments vary by manufacturer

Approaches to consider:

1. **Single pigment matching** - Map target color to nearest single pigment. Many watercolor brands publish pigment databases with approximate LAB values. handprint.com has extensive data.

2. **Kubelka-Munk model** - Mathematical model for how pigments mix. Could build a small database of your actual paints and their optical properties.

3. **Lookup table approach** - Photograph swatches of your paints and common mixtures, build an empirical mapping.

4. **Commercial resources** - Golden Paints and Gamblin have done computational work on pigment mixing.

### Temporal/Lighting Normalization

A photo at golden hour vs. noon gives very different palettes of the "same" place. Options:
- Note time-of-day in metadata
- Deliberately sample across lighting conditions for robustness
- Apply white balance normalization before extraction
- Separate "golden hour palette" vs "midday palette" as distinct aspects of a place

### Cross-Place Comparison Framework

Once you have multiple places (Santa Fe, Albania, future destinations), how to compare them systematically?

- **Earth Mover's Distance** - Measures how much "work" to transform one palette distribution into another
- **Signature vectors** - Average chroma, average lightness, dominant hue angles as a compact place descriptor
- **Palette embedding** - Project palettes into a space where similar places cluster together

---

## Existing Tools & Research

Worth being aware of:

- **Adobe Color** (formerly Kuler) - Has palette extraction from images
- **Coolors.co** - Similar web tool
- **"Colors of Motion"** - Project that extracts color sequences from films
- **Academic work** on color naming, color semantics, and computational color harmony
- **handprint.com** - Extensive watercolor pigment database with measured values

---

## Recommended Next Steps

1. **Semantic segmentation** - Highest value addition for distinguishing architectural vs. natural palettes

2. **Pigment database** - Start building a reference of your actual paints with measured LAB values (photograph swatches under consistent lighting)

3. **Color naming layer** - Add human-readable names to extracted colors

4. **Refactor to modules** - Move core functions from notebook to `scripts/` for reuse
