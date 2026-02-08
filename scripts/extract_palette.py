#!/usr/bin/env python3
"""Extract color palettes from place photographs.

Examples:
    # Single place, default settings
    python scripts/extract_palette.py santafe

    # Multiple places, 10 colors
    python scripts/extract_palette.py santafe abiqui shiprock --n-colors 10

    # All places in data/images/
    python scripts/extract_palette.py --all --n-colors 6

    # With accent palette
    python scripts/extract_palette.py santafe --accent --accent-colors 4 --chroma-percentile 85

    # Custom pixels per image and output directory
    python scripts/extract_palette.py santafe --pixels-per-image 10000 --output-dir output/palettes
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running from project root: `python scripts/extract_palette.py`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from glo.extract import (
    extract_accent_palette,
    kmeans_palette_from_lab_pixels,
    sample_lab_pixels_from_images,
)
from glo.io import find_photos, save_palette_image


def resolve_places(args) -> list[tuple[str, Path]]:
    """Return list of (place_name, place_dir) from CLI arguments."""
    images_root = PROJECT_ROOT / "data" / "images"

    if args.all:
        dirs = sorted(
            d for d in images_root.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        if args.exclude:
            exclude = set(args.exclude)
            dirs = [d for d in dirs if d.name not in exclude]
        return [(d.name, d) for d in dirs]

    places = []
    for name in args.places:
        place_dir = images_root / name
        if not place_dir.is_dir():
            print(f"Warning: place directory not found: {place_dir}", file=sys.stderr)
            continue
        places.append((name, place_dir))
    return places


def extract_for_place(name, place_dir, args):
    """Extract and save palette(s) for a single place."""
    photos = find_photos(place_dir)
    if not photos:
        print(f"  {name}: no photos found, skipping")
        return None

    print(f"  {name}: {len(photos)} photos")

    # Sample LAB pixels
    lab_pixels = sample_lab_pixels_from_images(
        photos,
        pixels_per_image=args.pixels_per_image,
        max_dim=args.max_dim,
    )

    # Main palette
    centers, counts = kmeans_palette_from_lab_pixels(
        lab_pixels, n_colors=args.n_colors
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save palette strip image
    img_path = output_dir / f"{name}_palette.png"
    save_palette_image(centers, counts, img_path)
    print(f"    palette -> {img_path}")

    result = {
        "name": name,
        "n_photos": len(photos),
        "n_colors": args.n_colors,
        "colors": [
            {
                "rgb": [int(c) for c in row],
                "proportion": round(float(cnt) / float(counts.sum()), 4),
            }
            for row, cnt in zip(centers, counts)
        ],
    }

    # Accent palette
    if args.accent:
        acc_centers, acc_counts = extract_accent_palette(
            lab_pixels,
            n_colors=args.accent_colors,
            chroma_percentile=args.chroma_percentile,
        )
        acc_path = output_dir / f"{name}_accent.png"
        save_palette_image(acc_centers, acc_counts, acc_path)
        print(f"    accent  -> {acc_path}")

        result["accent_colors"] = [
            {
                "rgb": [int(c) for c in row],
                "proportion": round(float(cnt) / float(acc_counts.sum()), 4),
            }
            for row, cnt in zip(acc_centers, acc_counts)
        ]

    # Save JSON sidecar
    json_path = output_dir / f"{name}_palette.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"    json    -> {json_path}")

    return {"name": name, "centers": centers, "counts": counts}


def main():
    parser = argparse.ArgumentParser(
        description="Extract color palettes from place photographs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else "",
    )

    # Place selection
    parser.add_argument(
        "places", nargs="*", default=[],
        help="Place folder names (e.g., santafe abiqui shiprock)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Process all place directories in data/images/",
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[],
        help="Exclude these places when using --all (e.g., --exclude albania)",
    )

    # Extraction parameters
    parser.add_argument(
        "--n-colors", type=int, default=8,
        help="Number of palette colors (default: 8)",
    )
    parser.add_argument(
        "--pixels-per-image", type=int, default=5000,
        help="LAB pixels sampled per image (default: 5000)",
    )
    parser.add_argument(
        "--max-dim", type=int, default=800,
        help="Max image dimension for loading (default: 800)",
    )

    # Accent palette
    parser.add_argument(
        "--accent", action="store_true",
        help="Also extract high-chroma accent palette",
    )
    parser.add_argument(
        "--accent-colors", type=int, default=4,
        help="Number of accent colors (default: 4)",
    )
    parser.add_argument(
        "--chroma-percentile", type=float, default=85.0,
        help="Chroma percentile threshold for accent extraction (default: 85.0)",
    )

    # Output
    parser.add_argument(
        "--output-dir", type=str, default="output/palettes",
        help="Output directory (default: output/palettes)",
    )

    args = parser.parse_args()

    if not args.places and not args.all:
        parser.error("Specify place names or use --all")

    places = resolve_places(args)
    if not places:
        print("No places to process.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting palettes for {len(places)} place(s):\n")

    for name, place_dir in places:
        extract_for_place(name, place_dir, args)
        print()


if __name__ == "__main__":
    main()
