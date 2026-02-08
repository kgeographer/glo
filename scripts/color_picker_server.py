#!/usr/bin/env python3
"""Local web server for manually picking color palettes from place photos."""

import json
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from glo.io import PHOTO_EXTS, find_photos, save_palette_image

IMAGES_DIR = PROJECT_ROOT / "data" / "images"
OUTPUT_DIR = PROJECT_ROOT / "output" / "palettes"

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "picker.html")


@app.route("/api/places")
def list_places():
    places = sorted(
        d.name for d in IMAGES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    return jsonify(places)


@app.route("/api/places/<name>/images")
def list_images(name):
    place_dir = IMAGES_DIR / name
    if not place_dir.is_dir():
        return jsonify({"error": "place not found"}), 404
    photos = find_photos(place_dir)
    filenames = [p.name for p in photos]
    return jsonify(filenames)


@app.route("/images/<name>/<filename>")
def serve_image(name, filename):
    place_dir = IMAGES_DIR / name
    path = place_dir / filename
    if not path.is_file() or path.suffix.lower() not in PHOTO_EXTS:
        return "not found", 404
    return send_file(path)


@app.route("/api/palettes/<name>", methods=["POST"])
def save_palette(name):
    data = request.get_json()
    colors = data.get("colors", [])
    if not colors:
        return jsonify({"error": "no colors provided"}), 400

    centers = np.array(colors, dtype=np.uint8)
    counts = np.ones(len(colors), dtype=np.int64)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    img_path = OUTPUT_DIR / f"{name}_picked.png"
    save_palette_image(centers, counts, img_path)

    json_path = OUTPUT_DIR / f"{name}_picked.json"
    result = {
        "name": name,
        "source": "manual",
        "n_colors": len(colors),
        "colors": [{"rgb": c} for c in colors],
    }
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    return jsonify({"saved": str(img_path), "json": str(json_path)})


if __name__ == "__main__":
    print(f"Serving images from: {IMAGES_DIR}")
    print(f"Saving palettes to:  {OUTPUT_DIR}")
    app.run(host="127.0.0.1", port=5050, debug=True)
