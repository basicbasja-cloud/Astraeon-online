#!/usr/bin/env python3
"""Include visible face pixels in the HeadHair cutout group.

Color segmentation often marks the hair but leaves warm facial pixels in the
base layer. This pass moves only skin-toned BaseBody pixels immediately below
each frame's hair mask into HeadHair. It never changes master art or alpha.
The output remains a template: review every camera direction before swaps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from cutout_master_sheet import CELL, SHEET, frame_count_for_size


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refine_headhair_labels(
    master_path: Path,
    labels_path: Path,
    output_path: Path,
    preview_path: Path | None = None,
    lower_padding_px: int = 7,
    horizontal_padding_px: int = 2,
) -> dict[str, Any]:
    """Move nearby warm BaseBody face pixels into HeadHair per 160px cell."""
    if lower_padding_px < 0 or horizontal_padding_px < 0:
        raise ValueError("ROI padding values cannot be negative")
    with Image.open(master_path) as opened:
        master = opened.convert("RGBA")
    with Image.open(labels_path) as opened:
        labels_image = opened.convert("L")
    source_labels_hash = _sha256(labels_path)
    frame_count = frame_count_for_size(master.size)
    if labels_image.size != master.size:
        raise ValueError("Master and labels must use the exact same frame grid")

    rgba = np.asarray(master, dtype=np.uint8)
    labels = np.asarray(labels_image, dtype=np.uint8).copy()
    visible = rgba[:, :, 3] > 0
    if np.any(visible & (labels == 0)) or np.any((~visible) & (labels != 0)):
        raise ValueError("Input labels must exactly cover visible master pixels")

    counts: list[dict[str, int]] = []
    for frame_index in range(frame_count):
        for direction_index in range(8):
            y0, x0 = frame_index * CELL, direction_index * CELL
            cell_labels = labels[y0:y0 + CELL, x0:x0 + CELL]
            hair_y, hair_x = np.nonzero(cell_labels == 2)
            if not len(hair_x):
                counts.append({"frame_index": frame_index, "direction_index": direction_index,
                               "moved_pixels": 0, "reason": "no HeadHair pixels"})
                continue

            x_min = max(0, int(hair_x.min()) - horizontal_padding_px)
            x_max = min(CELL, int(hair_x.max()) + 1 + horizontal_padding_px)
            y_min = max(0, int(hair_y.min()))
            y_max = min(CELL, int(hair_y.max()) + 1 + lower_padding_px)
            roi_labels = cell_labels[y_min:y_max, x_min:x_max]
            roi_rgba = rgba[y0 + y_min:y0 + y_max, x0 + x_min:x0 + x_max]
            rgb = roi_rgba[:, :, :3].astype(np.int16)
            # Warm skin tones, including shaded pixels; neutral silver hair and
            # the already separate gold cape are excluded by this color test
            # and BaseBody class restriction.
            warm_skin = (
                (rgb[:, :, 0] >= rgb[:, :, 1] * 1.03)
                & (rgb[:, :, 1] >= rgb[:, :, 2] * 1.015)
                & (rgb[:, :, 0] >= 55)
                & (rgb[:, :, 1] >= 25)
                & (rgb[:, :, 2] >= 10)
            )
            move = (roi_labels == 1) & (roi_rgba[:, :, 3] > 0) & warm_skin
            moved = int(np.count_nonzero(move))
            roi_labels[move] = 2
            counts.append({"frame_index": frame_index, "direction_index": direction_index,
                           "moved_pixels": moved})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(labels, mode="L").save(output_path, format="PNG", optimize=False)
    if preview_path is not None:
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        colors = {
            1: (35, 100, 255), 2: (255, 35, 180), 3: (35, 235, 65),
            4: (20, 235, 235), 5: (255, 225, 30), 6: (255, 65, 35),
            7: (220, 220, 220),
        }
        preview = rgba.copy()
        for class_id, color in colors.items():
            selected = labels == class_id
            preview[selected, :3] = (
                preview[selected, :3].astype(np.float32) * 0.42
                + np.asarray(color, dtype=np.float32) * 0.58
            ).astype(np.uint8)
        Image.fromarray(preview, mode="RGBA").save(preview_path, format="PNG", optimize=False)

    moved_total = sum(item["moved_pixels"] for item in counts)
    return {
        "status": "HEADHAIR_LABELS_REFINED_REVIEW_REQUIRED",
        "master": {"file": str(master_path), "sha256": _sha256(master_path)},
        "source_labels": {"file": str(labels_path), "sha256": source_labels_hash},
        "output_labels": {"file": str(output_path), "sha256": _sha256(output_path)},
        "preview": None if preview_path is None else str(preview_path),
        "class_ids": {"BaseBody": 1, "HeadHair": 2},
        "method": "warm BaseBody pixels within the hair mask bounding box, padded by the configured pixels, are reassigned to HeadHair",
        "lower_padding_px": lower_padding_px,
        "horizontal_padding_px": horizontal_padding_px,
        "moved_face_candidate_pixels": moved_total,
        "frame_records": counts,
        "warnings": [
            "This geometric/color heuristic is a label seed, not a finished semantic mask.",
            "Inspect all eight directions for accidental skin-colored armor or neck pixels before using swaps.",
            "No hidden scalp or face pixels are generated; only visible master pixels are reassigned.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--lower-padding-px", type=int, default=7)
    parser.add_argument("--horizontal-padding-px", type=int, default=2)
    args = parser.parse_args()
    report = refine_headhair_labels(
        args.master, args.labels, args.output, args.preview,
        args.lower_padding_px, args.horizontal_padding_px,
    )
    report_path = args.output.with_name(args.output.stem + "-headhair-refinement-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"],
                      "moved_face_candidate_pixels": report["moved_face_candidate_pixels"],
                      "output_labels": report["output_labels"]["file"],
                      "report": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
