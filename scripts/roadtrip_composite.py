#!/usr/bin/env python3
"""Generate a composite grid of palettes for a road trip or thematic set.

Examples:
    # Southwest road trip, 2 rows of 5
    python scripts/roadtrip_composite.py \
        santafe abiqui shiprock tubacity windowrock \
        seligman grandcanyon redrock deathvalley eastbay \
        --cols 5 --output output/palettes/southwest_roadtrip.png

    # Fewer colors, with accent palettes
    python scripts/roadtrip_composite.py \
        santafe abiqui shiprock \
        --n-colors 6 --accent --cols 3

    # Custom strip size
    python scripts/roadtrip_composite.py \
        santafe abiqui --strip-width 500 --strip-height 100
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from glo.extract import (
    extract_accent_palette,
    kmeans_palette_from_lab_pixels,
    sample_lab_pixels_from_images,
)
from glo.io import find_photos
from glo.visualize import render_composite

# Folder names that should display as two words
_COMPOUND_NAMES = {
    "grandcanyon": "Grand Canyon",
    "deathvalley": "Death Valley",
    "redrock": "Red Rock",
    "windowrock": "Window Rock",
    "eastbay": "East Bay",
    "ghostranch": "Ghost Ranch",
    "santafe": "Santa Fe",
}


def _display_name(folder_name: str) -> str:
    """Convert a folder name to a human-readable display name."""
    if folder_name.lower() in _COMPOUND_NAMES:
        return _COMPOUND_NAMES[folder_name.lower()]
    return folder_name.replace("_", " ").title()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a composite palette grid for multiple places.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "places", nargs="+",
        help="Place folder names in display order (e.g., santafe abiqui shiprock)",
    )

    # Layout
    parser.add_argument("--cols", type=int, default=5, help="Columns in grid (default: 5)")
    parser.add_argument("--strip-width", type=int, default=400, help="Palette strip width in px (default: 400)")
    parser.add_argument("--strip-height", type=int, default=80, help="Palette strip height in px (default: 80)")

    # Extraction
    parser.add_argument("--n-colors", type=int, default=8, help="Colors per palette (default: 8)")
    parser.add_argument("--accent", action="store_true", help="Use accent (high-chroma) palettes instead")
    parser.add_argument("--accent-colors", type=int, default=5, help="Number of accent colors (default: 5)")
    parser.add_argument("--chroma-percentile", type=float, default=85.0, help="Chroma percentile for accent (default: 85)")
    parser.add_argument("--pixels-per-image", type=int, default=5000, help="LAB pixels per image (default: 5000)")
    parser.add_argument("--max-dim", type=int, default=800, help="Max image dimension (default: 800)")

    # Output
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output image path (default: output/palettes/composite.png)",
    )

    args = parser.parse_args()
    images_root = PROJECT_ROOT / "data" / "images"

    place_palettes = []
    palette_type = "accent" if args.accent else "main"

    print(f"Building {palette_type} composite for {len(args.places)} places:\n")

    for name in args.places:
        place_dir = images_root / name
        if not place_dir.is_dir():
            print(f"  {name}: directory not found, skipping", file=sys.stderr)
            continue

        photos = find_photos(place_dir)
        if not photos:
            print(f"  {name}: no photos, skipping", file=sys.stderr)
            continue

        lab_pixels = sample_lab_pixels_from_images(
            photos,
            pixels_per_image=args.pixels_per_image,
            max_dim=args.max_dim,
        )

        if args.accent:
            centers, counts = extract_accent_palette(
                lab_pixels,
                n_colors=args.accent_colors,
                chroma_percentile=args.chroma_percentile,
            )
        else:
            centers, counts = kmeans_palette_from_lab_pixels(
                lab_pixels, n_colors=args.n_colors,
            )

        # Display name: split known compounds, title case
        display_name = _display_name(name)
        place_palettes.append({
            "name": display_name,
            "centers": centers,
            "counts": counts,
        })
        print(f"  {display_name}: {len(photos)} photos -> {len(centers)} colors")

    if not place_palettes:
        print("No palettes extracted.", file=sys.stderr)
        sys.exit(1)

    # Render composite
    composite = render_composite(
        place_palettes,
        cols=args.cols,
        strip_width=args.strip_width,
        strip_height=args.strip_height,
    )

    output_path = Path(args.output) if args.output else Path("output/palettes/composite.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite.save(output_path)
    print(f"\nComposite saved -> {output_path}  ({composite.size[0]}x{composite.size[1]} px)")

    # Also save a JSON summary
    json_path = output_path.with_suffix(".json")
    summary = {
        "places": [
            {
                "name": p["name"],
                "n_colors": len(p["centers"]),
                "palette_type": palette_type,
                "colors": [
                    {"rgb": [int(c) for c in row]}
                    for row in p["centers"]
                ],
            }
            for p in place_palettes
        ],
        "layout": {"cols": args.cols, "rows": (len(place_palettes) + args.cols - 1) // args.cols},
    }
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON  -> {json_path}")


if __name__ == "__main__":
    main()
