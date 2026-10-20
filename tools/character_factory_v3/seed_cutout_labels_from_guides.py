#!/usr/bin/env python3
"""Create an editable first-pass cutout label map from per-frame guide masks.

Guide labels are fitted to each full-character master cell. Uncovered visible
pixels default to BaseBody, so every master pixel remains represented. Treat
the result as an annotation seed and inspect/fix it with cutout_label_editor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from cutout_master_sheet import CELL, SHEET, frame_count_for_size


GROUP_TO_LABEL = {
    "BodyOutfit": 1,
    "HeadHair": 2,
    "Weapon": 4,
    "Cape": 5,
    "Headgear": 7,
    "Offhand": 1,
}


def _mask_labels(path: Path, colors: dict[str, list[int]]) -> Image.Image:
    with Image.open(path) as opened:
        rgba = np.asarray(opened.convert("RGBA"), dtype=np.uint8)
    labels = np.zeros(rgba.shape[:2], dtype=np.uint8)
    for group, class_id in GROUP_TO_LABEL.items():
        color = colors.get(group)
        if color is None:
            continue
        match = (rgba[:, :, 3] > 0) & np.all(rgba[:, :, :3] == np.asarray(color, dtype=np.uint8), axis=2)
        labels[match] = class_id
    return Image.fromarray(labels, mode="L")


def _bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    y, x = np.nonzero(mask)
    if not len(x):
        return None
    return int(x.min()), int(y.min()), int(x.max() + 1), int(y.max() + 1)


def _fit_labels_to_master(source: Image.Image, target_alpha: Image.Image) -> tuple[Image.Image, dict[str, Any]]:
    values = np.asarray(source.convert("L"), dtype=np.uint8)
    source_box = _bbox(values > 0)
    target_alpha_array = np.asarray(target_alpha, dtype=np.uint8) > 0
    target_box = _bbox(target_alpha_array)
    if source_box is None or target_box is None:
        raise ValueError("Guide segmentation and master cell must both contain visible pixels")
    sx0, sy0, sx1, sy1 = source_box
    tx0, ty0, tx1, ty1 = target_box
    sw, sh = sx1 - sx0, sy1 - sy0
    tw, th = tx1 - tx0, ty1 - ty0
    scale = min(tw / sw, th / sh)
    size = (max(1, round(source.width * scale)), max(1, round(source.height * scale)))
    resized = source.resize(size, Image.Resampling.NEAREST)
    scaled_box = (round(sx0 * scale), round(sy0 * scale), round(sx1 * scale), round(sy1 * scale))
    left = round((tx0 + tx1) / 2 - (scaled_box[0] + scaled_box[2]) / 2)
    top = round(ty1 - scaled_box[3])
    fitted = Image.new("L", (CELL, CELL), 0)
    fitted.paste(resized, (left, top))
    return fitted, {
        "guide_bbox": list(source_box),
        "master_bbox": list(target_box),
        "uniform_fit_scale": round(scale, 6),
        "translation": [left, top],
    }


def seed_cutout_labels(master_path: Path, guide_manifest_path: Path, action: str, output_path: Path) -> dict[str, Any]:
    with Image.open(master_path) as opened:
        master = opened.convert("RGBA")
    frame_count = frame_count_for_size(master.size)
    if master.getchannel("A").getextrema()[0] != 0:
        raise ValueError("Master sheet must have transparent background pixels")
    manifest = json.loads(guide_manifest_path.read_text(encoding="utf-8"))
    colors = manifest["segmentation"]["colors_rgb"]
    frames = {(item["frame_index"], item["direction"]): item for item in manifest["frames"]
              if item["action"] == action}
    directions = manifest["directions"]
    if len(frames) != frame_count * len(directions):
        raise ValueError(f"Guide manifest does not contain a {frame_count}-frame {action} action")

    output = np.zeros((frame_count * CELL, SHEET), dtype=np.uint8)
    frame_records = []
    for frame_index in range(frame_count):
        for direction_index, direction in enumerate(directions):
            source_record = frames[(frame_index, direction)]
            segmentation_path = guide_manifest_path.parent / source_record["passes"]["body_segmentation"]["file"]
            source_labels = _mask_labels(segmentation_path, colors)
            box = (direction_index * CELL, frame_index * CELL,
                   (direction_index + 1) * CELL, (frame_index + 1) * CELL)
            master_cell = master.crop(box)
            fitted, transform = _fit_labels_to_master(source_labels, master_cell.getchannel("A"))
            labels = np.asarray(fitted, dtype=np.uint8).copy()
            visible = np.asarray(master_cell.getchannel("A"), dtype=np.uint8) > 0
            inside_master = visible & (labels > 0)
            # Guide masks give a part map. Unmatched pixels remain with the
            # body group until an artist refines them in the label editor.
            labels[visible & ~inside_master] = 1
            labels[~visible] = 0
            output[frame_index * CELL:(frame_index + 1) * CELL,
                   direction_index * CELL:(direction_index + 1) * CELL] = labels
            frame_records.append({"frame_index": frame_index, "direction": direction,
                                  **transform, "master_visible_pixels": int(visible.sum()),
                                  "guide_seeded_pixels": int(inside_master.sum()),
                                  "body_default_pixels": int((visible & ~inside_master).sum())})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output, mode="L").save(output_path, format="PNG", optimize=False)
    report = {
        "status": "GUIDE_SEEDED_LABELS_NEEDS_ARTIST_REVIEW",
        "master": str(master_path),
        "guide_manifest": str(guide_manifest_path),
        "action": action,
        "output": str(output_path),
        "directions": directions,
        "class_ids": {"1": "BaseBody", "2": "HeadHair", "3": "Outfit", "4": "Weapon",
                      "5": "BackAccessory", "6": "CosmeticFX", "7": "Headgear"},
        "seed_policy": "Fit V3 guide segmentation per pose to the full-master silhouette. Uncovered pixels default to BaseBody. This is a rough label seed, not approved segmentation.",
        "frames": frame_records,
    }
    report_path = output_path.with_name(output_path.stem + "-seed-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--guide-manifest", type=Path, required=True)
    parser.add_argument("--action", choices=("Idle", "Walk", "BasicAttack"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = seed_cutout_labels(args.master, args.guide_manifest, args.action, args.output)
    print(json.dumps({"status": report["status"], "action": report["action"],
                      "output": report["output"], "report": str(args.output.with_name(args.output.stem + "-seed-report.json"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
