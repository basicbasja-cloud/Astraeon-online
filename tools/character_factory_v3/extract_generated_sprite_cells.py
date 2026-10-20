#!/usr/bin/env python3
"""Extract overlapping generated atlas figures into registered whole-frame cells.

Some image generators paint checkerboards and let character silhouettes cross
the nominal grid edges. This tool keys the edge-connected checkerboard, assigns
each whole foreground component to the nearest 4x4 cell, and packs the complete
figure into a padded transparent cell before the normal frame/foot registration
stage. It does not infer semantic outfit or body layers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.character_factory_v3.prepare_basicattack_sheet import (  # noqa: E402
    clean_cell,
    find_foot_baseline,
    resize_rgba,
)


def edge_connected(mask: np.ndarray) -> np.ndarray:
    edge = np.zeros(mask.shape, dtype=bool)
    edge[[0, -1], :] = mask[[0, -1], :]
    edge[:, [0, -1]] = mask[:, [0, -1]]
    return ndimage.binary_propagation(edge, mask=mask, structure=np.ones((3, 3), dtype=bool))


def checker_background(rgb: np.ndarray) -> np.ndarray:
    values = rgb.astype(np.int16)
    maximum, minimum = values.max(axis=2), values.min(axis=2)
    candidate = (maximum - minimum <= 40) & (minimum >= 120)
    return edge_connected(candidate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cell-size", type=int, default=512)
    parser.add_argument("--scale", type=float, default=1.1,
                        help="Shared source-to-output scale; never changes per-frame character scale")
    parser.add_argument("--root-x", type=int, default=256)
    parser.add_argument("--root-y", type=int, default=422)
    parser.add_argument("--component-min-area", type=int, default=10000)
    parser.add_argument("--small-component-distance", type=float, default=235.0)
    args = parser.parse_args()
    if min(args.columns, args.rows, args.cell_size, args.component_min_area) < 1 or args.scale <= 0:
        parser.error("grid, cell size, component area, and scale must be positive")

    source = Image.open(args.input).convert("RGB")
    rgb = np.asarray(source, dtype=np.uint8)
    height, width = rgb.shape[:2]
    edges_x = [round(i * width / args.columns) for i in range(args.columns + 1)]
    edges_y = [round(i * height / args.rows) for i in range(args.rows + 1)]
    background = checker_background(rgb)
    foreground = ~background
    labels, count = ndimage.label(foreground, structure=np.ones((3, 3), dtype=bool))
    sizes = np.bincount(labels.ravel())
    major_ids = [int(i) for i in np.flatnonzero(sizes >= args.component_min_area) if i]
    expected = args.columns * args.rows
    if len(major_ids) != expected:
        raise RuntimeError(f"expected {expected} whole characters, found {len(major_ids)} major components")

    centers: list[tuple[float, float]] = []
    for row in range(args.rows):
        for column in range(args.columns):
            centers.append(((edges_x[column] + edges_x[column + 1]) / 2,
                            (edges_y[row] + edges_y[row + 1]) / 2))

    major_by_cell: dict[int, int] = {}
    component_info: dict[int, dict[str, object]] = {}
    for component_id in major_ids:
        ys, xs = np.where(labels == component_id)
        centroid = (float(xs.mean()), float(ys.mean()))
        cell = min(range(expected), key=lambda index:
                   (centroid[0] - centers[index][0]) ** 2 + (centroid[1] - centers[index][1]) ** 2)
        if cell in major_by_cell:
            raise RuntimeError(f"two major figure components map to sprite cell {cell}")
        major_by_cell[cell] = component_id
        component_info[component_id] = {
            "area": int(sizes[component_id]),
            "bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)],
            "centroid_xy": [round(centroid[0], 2), round(centroid[1], 2)],
            "cell": cell,
        }
    if set(major_by_cell) != set(range(expected)):
        raise RuntimeError(f"major components did not cover all cells: {sorted(major_by_cell)}")

    assigned_small: dict[int, list[int]] = {cell: [] for cell in range(expected)}
    for component_id in range(1, count + 1):
        if component_id in component_info or sizes[component_id] < 3:
            continue
        ys, xs = np.where(labels == component_id)
        centroid = (float(xs.mean()), float(ys.mean()))
        cell = min(range(expected), key=lambda index:
                   (centroid[0] - centers[index][0]) ** 2 + (centroid[1] - centers[index][1]) ** 2)
        major_centroid = component_info[major_by_cell[cell]]["centroid_xy"]
        distance = float(np.hypot(centroid[0] - major_centroid[0], centroid[1] - major_centroid[1]))
        if distance <= args.small_component_distance:
            assigned_small[cell].append(component_id)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = args.output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (args.columns * args.cell_size, args.rows * args.cell_size), (0, 0, 0, 0))
    reports = []
    for cell in range(expected):
        component_ids = [major_by_cell[cell], *assigned_small[cell]]
        mask = np.isin(labels, component_ids)
        ys, xs = np.where(mask)
        source_bbox = (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1))
        source_rgba = np.dstack((rgb, np.where(mask, 255, 0).astype(np.uint8)))
        crop = Image.fromarray(source_rgba, "RGBA").crop(source_bbox)
        clean, fringe_pixels, debris_pixels = clean_cell(crop, debris_limit=12)
        boot_baseline, baseline_method = find_foot_baseline(clean)
        resize_size = (max(1, round(clean.width * args.scale)),
                       max(1, round(clean.height * args.scale)))
        resized = resize_rgba(clean, resize_size)
        column, row = cell % args.columns, cell // args.columns
        source_center_x = (edges_x[column] + edges_x[column + 1]) / 2
        baseline_y = source_bbox[1] + boot_baseline
        left = round(args.root_x + (source_bbox[0] - source_center_x) * args.scale)
        top = round(args.root_y + (source_bbox[1] - baseline_y) * args.scale)
        if left < 0 or top < 0 or left + resized.width > args.cell_size or top + resized.height > args.cell_size:
            raise RuntimeError(f"cell {cell} does not fit at the shared scale/root: {(left, top, *resize_size)}")
        frame = Image.new("RGBA", (args.cell_size, args.cell_size), (0, 0, 0, 0))
        frame.alpha_composite(resized, (left, top))
        frame.save(frames_dir / f"se_{cell:02d}.png")
        atlas.alpha_composite(frame, (column * args.cell_size, row * args.cell_size))
        reports.append({
            "frame_index": cell,
            "major_component": component_info[major_by_cell[cell]],
            "attached_components": assigned_small[cell],
            "source_character_bbox_xyxy": list(source_bbox),
            "foot_baseline_y_px": int(baseline_y),
            "foot_baseline_method": baseline_method,
            "shared_scale": args.scale,
            "output_root_xy": [args.root_x, args.root_y],
            "output_placement_xy": [left, top],
            "removed_red_fringe_pixels": fringe_pixels,
            "removed_small_components_pixels": debris_pixels,
        })
    atlas_path = args.output_dir / "whole-character-master-atlas.png"
    atlas.save(atlas_path, optimize=True)
    report = {
        "status": "REVIEW_ONLY_WHOLE_CHARACTER_CELLS",
        "input": str(args.input.resolve()),
        "grid": [args.columns, args.rows],
        "source_size": [width, height],
        "source_cell_edges_x": edges_x,
        "source_cell_edges_y": edges_y,
        "checker_pixels_removed": int(background.sum()),
        "shared_scale": args.scale,
        "cell_size": args.cell_size,
        "root_xy": [args.root_x, args.root_y],
        "atlas": str(atlas_path.resolve()),
        "semantic_layers_created": False,
        "frames": reports,
        "limitations": [
            "Connected-component extraction repairs grid-boundary bleed but does not validate guide pose fidelity.",
            "Each result remains a whole-character frame; semantic modular layers are not yet cut.",
        ],
    }
    report_path = args.output_dir / "extraction-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"atlas": str(atlas_path.resolve()), "frames": expected,
                      "checker_pixels_removed": int(background.sum()),
                      "report": str(report_path.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
