#!/usr/bin/env python3
"""Cut a full-character 8-by-N master sheet into aligned per-part pixel layers.

The label sheet is authored over the exact master frames. Every visible master
pixel belongs to one layer id, so recomposition restores the source master
pixel-for-pixel. This creates cutout templates; it does not invent hidden art.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


CELL = 160
DIRECTION_COUNT = 8
SHEET = CELL * DIRECTION_COUNT  # sheet width; frame rows are variable
LABELS = {
    1: ("BaseBody", "BaseBody"),
    2: ("HeadHair", "Hair"),
    3: ("Outfit", "Outfit"),
    4: ("Weapon", "Weapon"),
    5: ("BackAccessory", "BackAccessory"),
    6: ("CosmeticFX", "CosmeticFX"),
    7: ("Headgear", "Headgear"),
}


def frame_count_for_size(size: tuple[int, int]) -> int:
    width, height = size
    if width != SHEET or height < CELL * 2 or height % CELL:
        raise ValueError(f"Expected an 8-column sheet with 160px cells: {size}")
    return height // CELL
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_master_and_labels(master_path: Path, labels_path: Path) -> tuple[Image.Image, Image.Image]:
    with Image.open(master_path) as source:
        master = source.convert("RGBA")
    with Image.open(labels_path) as source:
        label_sheet = source.convert("L")
    frame_count = frame_count_for_size(master.size)
    if master.getchannel("A").getextrema()[0] != 0:
        raise ValueError(f"Master sheet needs transparent background pixels: {master_path}")
    if label_sheet.size != master.size:
        raise ValueError(f"Master/labels size mismatch: {master_path} {master.size}, {labels_path} {label_sheet.size}")
    valid_ids = {0, *LABELS.keys()}
    unique_ids = set(np.unique(np.asarray(label_sheet, dtype=np.uint8)).tolist())
    unknown = sorted(unique_ids - valid_ids)
    if unknown:
        raise ValueError(f"Unknown class ids {unknown} in {labels_path}; known ids: {sorted(valid_ids)}")
    return master, label_sheet


def _extract_layers(master: Image.Image, labels: Image.Image) -> tuple[dict[str, Image.Image], dict[str, Any]]:
    rgba = np.asarray(master.convert("RGBA"), dtype=np.uint8)
    ids = np.asarray(labels.convert("L"), dtype=np.uint8)
    visible = rgba[:, :, 3] > 0
    unassigned = visible & (ids == 0)
    outside = (~visible) & (ids != 0)
    if np.any(unassigned):
        y, x = np.argwhere(unassigned)[0]
        raise ValueError(f"Master has visible but unlabelled pixels: {int(np.count_nonzero(unassigned))}; first at x={x}, y={y}")
    if np.any(outside):
        y, x = np.argwhere(outside)[0]
        raise ValueError(f"Label sheet paints transparent master pixels: {int(np.count_nonzero(outside))}; first at x={x}, y={y}")

    layers: dict[str, Image.Image] = {}
    label_counts: dict[str, int] = {}
    reconstructed = np.zeros_like(rgba)
    for class_id, (label_name, output_name) in LABELS.items():
        part = rgba.copy()
        mask = ids == class_id
        part[~mask, 3] = 0
        layers[output_name] = Image.fromarray(part, mode="RGBA")
        label_counts[label_name] = int(np.count_nonzero(mask))
        selected = reconstructed[:, :, 3] == 0
        apply = mask & selected
        reconstructed[apply] = rgba[apply]

    if not np.array_equal(reconstructed, rgba):
        raise ValueError("Cutout layers do not recompose to the master sheet exactly")
    return layers, {
        "visible_source_pixels": int(np.count_nonzero(visible)),
        "label_pixel_counts": label_counts,
        "unassigned_visible_pixels": 0,
        "labels_outside_master_alpha": 0,
        "reconstruction_mismatch_pixels": 0,
        "reconstruction": "exact pixel-for-pixel from disjoint labels; hidden surfaces are not generated",
    }


def cutout_master_sheet(
    input_root: Path,
    output_root: Path,
    actions: list[str],
) -> dict[str, Any]:
    if not actions:
        raise ValueError("Select at least one action")
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "CUTOUT_TEMPLATE_REVIEW_ONLY",
        "workflow": "one full-character master per action, cut into aligned layers from that same frame sheet",
        "layout": "eight directions as columns, variable chronological frame rows",
        "runtime_cell_px": [CELL, CELL],
        "layers": {str(class_id): {"name": label_name, "output_folder": output_name}
                   for class_id, (label_name, output_name) in LABELS.items()},
        "actions": {},
        "warnings": [
            "Cutouts preserve only pixels visible in the master; no hidden body, scalp, or outfit surface is invented.",
            "Draw replacement outfits or hair from these exact per-frame masks and fill concealed base surfaces before enabling swaps.",
            "The source motion and frame order remain unchanged.",
            "This output is review material and is not a runtime package.",
        ],
    }
    for action in actions:
        action_dir = input_root / action
        master_path = action_dir / "master.png"
        labels_path = action_dir / "labels.png"
        if not master_path.is_file() or not labels_path.is_file():
            raise FileNotFoundError(f"Expected both {master_path} and {labels_path}")
        master, labels = _load_master_and_labels(master_path, labels_path)
        layers, metrics = _extract_layers(master, labels)
        frame_count = frame_count_for_size(master.size)
        for layer, sheet in layers.items():
            target = output_root / layer / f"{action.lower()}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(target, format="PNG", optimize=False)
        report["actions"][action] = {
            "frame_count": frame_count,
            "master": {"file": str(master_path), "sha256": _sha256(master_path)},
            "labels": {"file": str(labels_path), "sha256": _sha256(labels_path)},
            "layers": metrics,
        }
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "cutout-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def write_label_template(master_path: Path, target: Path) -> None:
    with Image.open(master_path) as source:
        image = source.convert("RGBA")
    frame_count_for_size(image.size)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.new("L", image.size, 0).save(target, format="PNG", optimize=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True,
                        help="Contains <Action>/master.png and <Action>/labels.png")
    parser.add_argument("--output-root", type=Path, required=True,
                        help="Receives <Layer>/<action>.png sheets and cutout-report.json")
    parser.add_argument("--actions", nargs="+", required=True,
                        choices=("Idle", "Walk", "BasicAttack"))
    parser.add_argument("--write-label-templates", action="store_true",
                        help="Create empty labels.png files alongside masters that have no labels yet")
    args = parser.parse_args()
    if args.write_label_templates:
        created = []
        for action in args.actions:
            action_dir = args.input_root / action
            master_path = action_dir / "master.png"
            if not master_path.is_file():
                raise FileNotFoundError(master_path)
            labels_path = action_dir / "labels.png"
            if not labels_path.exists():
                write_label_template(master_path, labels_path)
                created.append(str(labels_path))
        print(json.dumps({"status": "LABEL_TEMPLATES_READY_FOR_ANNOTATION",
                          "templates": created,
                          "label_values": {str(class_id): label for class_id, (label, _) in LABELS.items()}}, indent=2))
        return 0
    report = cutout_master_sheet(args.input_root, args.output_root, args.actions)
    print(json.dumps({"status": report["status"], "actions": list(report["actions"]),
                      "output_root": str(args.output_root),
                      "report": str(args.output_root / "cutout-report.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
