#!/usr/bin/env python3
"""Clean detached cross-cell scraps and apply one shared root transform.

The transform is measured from the full 8x8 master and applied identically to
every frame. Isolated body/outfit scraps above the main character are removed,
then the same affine transform is applied to master RGBA pixels and labels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image

from cutout_master_sheet import CELL, SHEET, frame_count_for_size


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _components(mask: np.ndarray) -> list[np.ndarray]:
    height, width = mask.shape
    seen = np.zeros((height, width), dtype=bool)
    found: list[np.ndarray] = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or seen[y, x]:
                continue
            seen[y, x] = True
            stack = [(y, x)]
            points: list[tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                points.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if not (dx or dy):
                            continue
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
            found.append(np.asarray(points, dtype=np.int16))
    return sorted(found, key=len, reverse=True)


def _bounds(points: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = points[:, 0], points[:, 1]
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def _transform_float(image: Image.Image, affine: tuple[float, float, float, float, float, float]) -> np.ndarray:
    transformed = image.transform((CELL, CELL), Image.Transform.AFFINE, affine,
                                  resample=Image.Resampling.BICUBIC)
    return np.asarray(transformed, dtype=np.float32)


def _transform_rgba(cell: Image.Image, affine: tuple[float, float, float, float, float, float]) -> Image.Image:
    rgba = np.asarray(cell.convert("RGBA"), dtype=np.float32)
    alpha = rgba[:, :, 3] / 255.0
    alpha_image = Image.fromarray((alpha * 255.0).astype(np.float32), mode="F")
    transformed_alpha = np.clip(_transform_float(alpha_image, affine), 0.0, 255.0)
    output = np.zeros((CELL, CELL, 4), dtype=np.uint8)
    output[:, :, 3] = np.rint(transformed_alpha).astype(np.uint8)
    for channel in range(3):
        premultiplied = Image.fromarray(rgba[:, :, channel] * alpha, mode="F")
        transformed = np.clip(_transform_float(premultiplied, affine), 0.0, 255.0)
        visible = transformed_alpha > 0.5
        channel_data = np.zeros((CELL, CELL), dtype=np.float32)
        channel_data[visible] = transformed[visible] * 255.0 / transformed_alpha[visible]
        output[:, :, channel] = np.clip(np.rint(channel_data), 0, 255).astype(np.uint8)
    output[output[:, :, 3] == 0, :3] = 0
    return Image.fromarray(output, mode="RGBA")


def _transform_labels(cell: Image.Image, affine: tuple[float, float, float, float, float, float], alpha: Image.Image) -> Image.Image:
    labels = cell.convert("L").transform((CELL, CELL), Image.Transform.AFFINE, affine,
                                         resample=Image.Resampling.NEAREST)
    values = np.asarray(labels, dtype=np.uint8).copy()
    visible = np.asarray(alpha, dtype=np.uint8) > 0
    values[visible & (values == 0)] = 1
    values[~visible] = 0
    return Image.fromarray(values, mode="L")


def normalize_master_sheet(
    master_path: Path,
    labels_path: Path,
    output_master_path: Path,
    output_labels_path: Path,
    reference_height: int = 112,
    root_anchor_x: int = 80,
    root_anchor_y: int = 132,
    fragment_limit: int = 500,
    shared_scale: float | None = None,
) -> dict[str, Any]:
    with Image.open(master_path) as opened:
        master = opened.convert("RGBA")
    with Image.open(labels_path) as opened:
        labels = opened.convert("L")
    frame_count = frame_count_for_size(master.size)
    if labels.size != master.size:
        raise ValueError("Master and labels must use the exact same frame grid")
    if master.getchannel("A").getextrema()[0] != 0:
        raise ValueError("Master sheet needs transparent background pixels")
    if not 1 <= reference_height < CELL:
        raise ValueError("reference_height must be between 1 and the cell size")
    if fragment_limit < 0:
        raise ValueError("fragment_limit cannot be negative")
    if shared_scale is not None and shared_scale <= 0:
        raise ValueError("shared_scale must be positive")

    rgba = np.asarray(master, dtype=np.uint8).copy()
    ids = np.asarray(labels, dtype=np.uint8).copy()
    original_visible_pixels = int(np.count_nonzero(rgba[:, :, 3]))
    records: list[dict[str, Any]] = []
    main_heights: list[int] = []
    main_bottoms: list[int] = []
    torso_centers: list[float] = []

    # First remove detached body/outfit pieces that sit above the character. This
    # catches small neighboring-cell remnants without touching weapon, cape,
    # head, or effect components.
    for frame_index in range(frame_count):
        for direction_index in range(8):
            y0, x0 = frame_index * CELL, direction_index * CELL
            alpha = rgba[y0:y0 + CELL, x0:x0 + CELL, 3] > 0
            cell_ids = ids[y0:y0 + CELL, x0:x0 + CELL]
            parts = _components(alpha)
            if not parts:
                raise ValueError(f"Empty master cell at frame {frame_index}, direction index {direction_index}")
            primary = parts[0]
            primary_box = _bounds(primary)
            primary_top = primary_box[1]
            removed = 0
            for component in parts[1:]:
                cy, cx = component[:, 0], component[:, 1]
                component_labels = cell_ids[cy, cx]
                component_bottom = int(cy.max() + 1)
                if (
                    len(component) <= fragment_limit
                    and component_bottom <= primary_top + 20
                    and np.all(np.isin(component_labels, (1, 3)))
                ):
                    rgba[y0 + cy, x0 + cx, 3] = 0
                    ids[y0 + cy, x0 + cx] = 0
                    removed += int(len(component))

            alpha = rgba[y0:y0 + CELL, x0:x0 + CELL, 3] > 0
            primary = _components(alpha)[0]
            primary_y, primary_x = primary[:, 0], primary[:, 1]
            primary_box = _bounds(primary)
            top, bottom = int(primary_y.min()), int(primary_y.max() + 1)
            main_heights.append(bottom - top)
            main_bottoms.append(bottom)

            # Measure one shared horizontal anchor from the same chest region
            # across views, so per-frame pose changes are not recentered away.
            height = bottom - top
            yy_grid = np.indices(cell_ids.shape)[0]
            center_region = np.isin(cell_ids, (1, 3)) & (yy_grid >= top + 0.30 * height) & (yy_grid <= top + 0.65 * height)
            center_region &= alpha
            _, chest_x = np.nonzero(center_region)
            if len(chest_x):
                torso_centers.append(float(np.median(chest_x)))
            records.append({
                "frame_index": frame_index,
                "direction_index": direction_index,
                "pretransform_primary_bbox": list(primary_box),
                "removed_detached_top_body_outfit_pixels": removed,
            })

    source_visible_pixels = int(np.count_nonzero(rgba[:, :, 3]))
    scale_policy = "shared project scale supplied by caller" if shared_scale is not None else "derived from this master median height"
    shared_scale = float(shared_scale) if shared_scale is not None else reference_height / float(median(main_heights))
    source_root_x = float(median(torso_centers)) if torso_centers else root_anchor_x
    source_root_y = float(median(main_bottoms))
    # PIL affine coefficients map each destination pixel back to the source.
    affine = (
        1.0 / shared_scale,
        0.0,
        source_root_x - root_anchor_x / shared_scale,
        0.0,
        1.0 / shared_scale,
        source_root_y - root_anchor_y / shared_scale,
    )

    source_master_image = Image.fromarray(rgba, mode="RGBA")
    source_labels_image = Image.fromarray(ids, mode="L")
    normalized_size = (SHEET, frame_count * CELL)
    normalized_master = Image.new("RGBA", normalized_size, (0, 0, 0, 0))
    normalized_labels = Image.new("L", normalized_size, 0)
    for frame_index in range(frame_count):
        for direction_index in range(8):
            y0, x0 = frame_index * CELL, direction_index * CELL
            box = (x0, y0, x0 + CELL, y0 + CELL)
            transformed = _transform_rgba(source_master_image.crop(box), affine)
            transformed_labels = _transform_labels(source_labels_image.crop(box), affine, transformed.getchannel("A"))
            normalized_master.alpha_composite(transformed, (x0, y0))
            normalized_labels.paste(transformed_labels, (x0, y0))

    output_master_path.parent.mkdir(parents=True, exist_ok=True)
    output_labels_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_master.save(output_master_path, format="PNG", optimize=False)
    normalized_labels.save(output_labels_path, format="PNG", optimize=False)
    normalized_visible_pixels = int(np.count_nonzero(np.asarray(normalized_master.getchannel("A"), dtype=np.uint8)))
    report = {
        "status": "MASTER_NORMALIZED_WITH_SHARED_SCALE_AND_ROOT",
        "source_master": {"file": str(master_path), "sha256": _sha256(master_path)},
        "source_labels": {"file": str(labels_path), "sha256": _sha256(labels_path)},
        "normalized_master": {"file": str(output_master_path), "sha256": _sha256(output_master_path)},
        "normalized_labels": {"file": str(output_labels_path), "sha256": _sha256(output_labels_path)},
        "cell_px": CELL,
        "frame_count": frame_count,
        "target_reference_height_px": reference_height,
        "root_anchor_px": [root_anchor_x, root_anchor_y],
        "shared_scale": round(shared_scale, 6),
        "scale_policy": scale_policy,
        "shared_source_anchor_px": [round(source_root_x, 3), round(source_root_y, 3)],
        "original_visible_pixels_before_fragment_cleanup": original_visible_pixels,
        "source_visible_pixels_after_fragment_cleanup": source_visible_pixels,
        "normalized_visible_pixels": normalized_visible_pixels,
        "source_primary_height_px_median_range": [
            min(main_heights), int(median(main_heights)), max(main_heights)
        ],
        "removed_detached_top_body_outfit_pixels": sum(item["removed_detached_top_body_outfit_pixels"] for item in records),
        "frame_records": records,
        "notes": [
            "One shared scale and one shared x/y affine transform are applied to every action frame and direction.",
            "Detached small BaseBody or Outfit fragments above the main character are cleared before normalization.",
            "Layer labels use nearest-neighbor sampling; uncovered visible edge pixels default to BaseBody.",
            "Check the review GIF for remaining pose, frame, and art-quality issues.",
        ],
    }
    report_path = output_master_path.with_name("master-normalization-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-master", type=Path, required=True)
    parser.add_argument("--output-labels", type=Path, required=True)
    parser.add_argument("--reference-height", type=int, default=112)
    parser.add_argument("--root-anchor", nargs=2, type=int, default=(80, 132), metavar=("X", "Y"))
    parser.add_argument("--fragment-limit", type=int, default=500)
    parser.add_argument("--shared-scale", type=float,
                        help="Use the same scale across action masters instead of deriving one from this sheet")
    args = parser.parse_args()
    report = normalize_master_sheet(
        args.master, args.labels, args.output_master, args.output_labels,
        args.reference_height, args.root_anchor[0], args.root_anchor[1], args.fragment_limit,
        args.shared_scale,
    )
    print(json.dumps({"status": report["status"], "shared_scale": report["shared_scale"],
                      "root_anchor_px": report["root_anchor_px"],
                      "removed_detached_top_body_outfit_pixels": report["removed_detached_top_body_outfit_pixels"],
                      "report": str(args.output_master.with_name("master-normalization-report.json"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
