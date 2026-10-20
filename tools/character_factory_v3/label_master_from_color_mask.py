#!/usr/bin/env python3
"""Convert a color-coded full-master segmentation image into pixel labels.

The master remains the sole source of art pixels. This tool reads class colors
from an aligned color mask, clips every class to the master's alpha, assigns
otherwise-unclassified visible pixels to BaseBody, and writes an editable label
map plus a diagnostic overlay. Inspect the result before accepting cutouts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from cutout_master_sheet import LABELS, frame_count_for_size


# RGB colors in the flat segmentation image -> master cutout class ids.
COLOR_CLASSES = {
    1: (0, 0, 255),       # BaseBody
    2: (255, 0, 255),     # HeadHair
    3: (0, 255, 0),       # Outfit
    4: (0, 255, 255),     # Weapon
    5: (255, 255, 0),     # BackAccessory
    6: (255, 0, 0),       # CosmeticFX
}
PREVIEW_COLORS = {
    1: (35, 100, 255),
    2: (255, 35, 180),
    3: (35, 235, 65),
    4: (20, 235, 235),
    5: (255, 225, 30),
    6: (255, 65, 35),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _classify_mask(mask_image: Image.Image, max_color_distance: float) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(mask_image.convert("RGB"), dtype=np.int32)
    class_ids = np.asarray([0, *COLOR_CLASSES.keys()], dtype=np.uint8)
    palette = np.asarray([(0, 0, 0), *COLOR_CLASSES.values()], dtype=np.int32)
    distances = np.sqrt(((rgb[:, :, None, :] - palette[None, None, :, :]) ** 2).sum(axis=3))
    nearest = distances.argmin(axis=2)
    closest_distance = distances.min(axis=2)
    labels = class_ids[nearest]
    labels[closest_distance > max_color_distance] = 0
    return labels, closest_distance


def _preview(master: Image.Image, labels: np.ndarray) -> Image.Image:
    rgba = np.asarray(master.convert("RGBA"), dtype=np.uint8).copy()
    for class_id, color in PREVIEW_COLORS.items():
        selected = labels == class_id
        rgba[selected, :3] = (
            rgba[selected, :3].astype(np.float32) * 0.42
            + np.asarray(color, dtype=np.float32) * 0.58
        ).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def color_mask_to_labels(
    master_path: Path,
    mask_path: Path,
    labels_path: Path,
    preview_path: Path | None = None,
    max_color_distance: float = 125.0,
) -> dict[str, Any]:
    with Image.open(master_path) as opened:
        master = opened.convert("RGBA")
    frame_count = frame_count_for_size(master.size)
    if master.getchannel("A").getextrema()[0] != 0:
        raise ValueError(f"Master sheet needs transparent background pixels: {master_path}")
    if max_color_distance <= 0:
        raise ValueError("max_color_distance must be positive")

    with Image.open(mask_path) as opened:
        color_mask = opened.convert("RGB")
    original_mask_size = list(color_mask.size)
    if color_mask.size != master.size:
        color_mask = color_mask.resize(master.size, Image.Resampling.BILINEAR)

    inferred, distances = _classify_mask(color_mask, max_color_distance)
    rgba = np.asarray(master, dtype=np.uint8)
    visible = rgba[:, :, 3] > 0
    inferred_before_clip = inferred.copy()
    inferred[~visible] = 0
    mask_outside_master = (~visible) & (inferred_before_clip > 0)
    unclassified_visible = visible & (inferred == 0)
    # The whole-character composite is the starting body layer; accessory and
    # head classes are carved from it only where the color mask identifies them.
    inferred[unclassified_visible] = 1

    labels_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(inferred, mode="L").save(labels_path, format="PNG", optimize=False)
    if preview_path is not None:
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        _preview(master, inferred).save(preview_path, format="PNG", optimize=False)

    class_counts = {
        LABELS[class_id][0]: int(np.count_nonzero(inferred == class_id))
        for class_id in LABELS
    }
    report = {
        "status": "COLOR_MASK_LABELS_NEEDS_VISUAL_REVIEW",
        "master": {"file": str(master_path), "sha256": _sha256(master_path)},
        "color_mask": {
            "file": str(mask_path),
            "sha256": _sha256(mask_path),
            "original_size": original_mask_size,
            "resized_to_master": color_mask.size != tuple(original_mask_size),
        },
        "labels": {"file": str(labels_path), "sha256": _sha256(labels_path)},
        "preview": None if preview_path is None else str(preview_path),
        "palette_rgb": {str(class_id): list(color) for class_id, color in COLOR_CLASSES.items()},
        "max_color_distance": max_color_distance,
        "master_visible_pixels": int(np.count_nonzero(visible)),
        "class_pixel_counts": class_counts,
        "color_mask_pixels_outside_master_alpha": int(np.count_nonzero(mask_outside_master)),
        "unclassified_visible_pixels_assigned_to_base_body": int(np.count_nonzero(unclassified_visible)),
        "unlabeled_visible_pixels": int(np.count_nonzero(visible & (inferred == 0))),
        "label_pixels_outside_master_alpha": int(np.count_nonzero((~visible) & (inferred > 0))),
        "notes": [
            "The color mask supplies labels only; all cutout RGB and alpha pixels come unchanged from the full master.",
            "Unclassified visible pixels are assigned to BaseBody so the source can be recomposed exactly.",
            "Generated mask boundaries and semantic classes still require visual review before part swaps.",
        ],
    }
    report_path = labels_path.with_name(labels_path.stem + "-color-mask-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--max-color-distance", type=float, default=125.0)
    args = parser.parse_args()
    report = color_mask_to_labels(args.master, args.mask, args.labels, args.preview, args.max_color_distance)
    print(json.dumps({"status": report["status"], "labels": report["labels"]["file"],
                      "class_pixel_counts": report["class_pixel_counts"],
                      "report": str(args.labels.with_name(args.labels.stem + "-color-mask-report.json"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
