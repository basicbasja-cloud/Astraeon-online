#!/usr/bin/env python3
"""Recover transparent character cutouts from generated checker/magenta backdrops."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from .prepare_basicattack_sheet import clean_cell


def edge_connected(mask: np.ndarray) -> np.ndarray:
    edge = np.zeros(mask.shape, dtype=bool)
    edge[[0, -1], :] = mask[[0, -1], :]
    edge[:, [0, -1]] = mask[:, [0, -1]]
    return ndimage.binary_propagation(
        edge, mask=mask, structure=np.ones((3, 3), dtype=bool)
    )


def remove_backdrop(image: Image.Image, kind: str) -> tuple[Image.Image, int]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8).astype(np.int16)
    if kind == "magenta":
        red, green, blue = (rgb[:, :, i] for i in range(3))
        candidate = (
            (red >= 145) & (blue >= 135) & (green <= 120)
            & (red - green >= 70) & (blue - green >= 60)
        )
    else:
        maximum = rgb.max(axis=2)
        minimum = rgb.min(axis=2)
        # The generator flattens its faux transparency grid at several neutral
        # brightness levels. Keep the component connected to the image border.
        candidate = (maximum - minimum <= 40) & (minimum >= 120)
    background = edge_connected(candidate)
    alpha = np.where(background, 0, 255).astype(np.uint8)
    rgba = Image.fromarray(np.dstack((rgb.astype(np.uint8), alpha)), "RGBA")
    cleaned, fringe, debris = clean_cell(rgba, debris_limit=256)
    pixels = np.asarray(cleaned).copy()
    pixels[pixels[:, :, 3] == 0] = 0
    return Image.fromarray(pixels, "RGBA"), int(background.sum())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--frames", type=int, default=16)
    parser.add_argument("--magenta-frames", default="",
                        help="Comma-separated zero-based frame indices with a solid magenta key")
    args = parser.parse_args()
    magenta = {int(value) for value in args.magenta_frames.split(",") if value.strip()}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = []
    for index in range(args.frames):
        source = args.input_dir / f"se_{index:02d}.png"
        output = args.output_dir / f"se_{index:02d}.png"
        cleaned, removed = remove_backdrop(Image.open(source),
                                            "magenta" if index in magenta else "checker")
        cleaned.save(output, optimize=True)
        report.append({"frame": index, "backdrop": "magenta" if index in magenta else "checker",
                       "removed_background_pixels": removed,
                       "alpha_bounds": list(cleaned.getchannel("A").getbbox() or [])})
    (args.output_dir / "cleanup-report.json").write_text(
        json.dumps({"method": "edge-connected checker/magenta key; alpha debris under 256 pixels removed",
                    "frames": report}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
