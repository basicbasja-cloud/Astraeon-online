#!/usr/bin/env python3
"""Normalize an image-generated 4x4 full-frame attack sheet for review."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


CELL = (160, 160)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_cell(cell: Image.Image) -> tuple[Image.Image, int, int]:
    """Drop isolated bright red image-generation fringe without repainting art."""
    rgba = np.asarray(cell.convert("RGBA")).copy()
    alpha = rgba[:, :, 3]
    red, green, blue = (rgba[:, :, channel].astype(np.int16) for channel in range(3))

    bright_red_fringe = (
        (alpha > 0)
        & (red >= 145)
        & (green <= 115)
        & (blue <= 165)
        & (red >= green * 1.35)
        & (red >= blue * 1.08)
    )
    magenta_fringe = (
        (alpha > 0)
        & (red >= 145)
        & (blue >= 145)
        & (green <= 105)
        & (red >= green * 1.35)
        & (blue >= green * 1.35)
    )
    fringe = bright_red_fringe | magenta_fringe
    fringe_pixels = int(fringe.sum())
    rgba[fringe, 3] = 0

    rgba[:, :, 3][rgba[:, :, 3] < 8] = 0
    components, count = ndimage.label(rgba[:, :, 3] > 0, structure=np.ones((3, 3), dtype=np.uint8))
    sizes = np.bincount(components.ravel())
    small = (sizes < 12)
    small[0] = False
    debris = small[components]
    debris_pixels = int(debris.sum())
    rgba[debris, 3] = 0
    return Image.fromarray(rgba, "RGBA"), fringe_pixels, debris_pixels


def write_sheet(frames: list[Image.Image], path: Path, columns: int) -> None:
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * CELL[0], rows * CELL[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % columns) * CELL[0], (index // columns) * CELL[1]))
    sheet.save(path)


def write_contact(frames: list[Image.Image], path: Path, columns: int) -> None:
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * CELL[0], rows * CELL[1]), (235, 235, 235, 255))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % columns) * CELL[0], (index // columns) * CELL[1]))
    sheet.convert("RGB").save(path)


def write_gif(frames: list[Image.Image], durations: list[int], path: Path, scale: int) -> int:
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", CELL, (235, 235, 235, 255))
        canvas.alpha_composite(frame)
        if scale != 1:
            canvas = canvas.resize((CELL[0] * scale, CELL[1] * scale), Image.Resampling.LANCZOS)
        canvases.append(canvas.convert("RGB"))

    palette_source = Image.new("RGB", (canvases[0].width, canvases[0].height * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * canvas.height))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in canvases]

    held = list(durations)
    held[-1] = max(held[-1], 600)
    units = [duration // 10 for duration in held]
    target_units = (sum(held) + 5) // 10
    remainder_units = target_units - sum(units)
    order = sorted(range(len(held)), key=lambda index: (-(held[index] % 10), index))
    for index in order[:remainder_units]:
        units[index] += 1
    encoded = [unit * 10 for unit in units]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=encoded, disposal=2, optimize=False)
    return sum(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--target-width", type=int, default=150)
    parser.add_argument("--target-height", type=int, default=112)
    parser.add_argument("--root-x", type=int, default=80)
    parser.add_argument("--root-y", type=int, default=132)
    parser.add_argument("--review-scale", type=int, default=3)
    args = parser.parse_args()
    if min(args.columns, args.rows, args.target_width, args.target_height, args.review_scale) < 1:
        parser.error("grid, target dimensions and review scale must be positive")

    source = Image.open(args.sheet).convert("RGBA")
    if source.width < args.columns or source.height < args.rows:
        parser.error(f"sheet size {source.size} is too small for {args.columns}x{args.rows}")
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    if len(timeline.get("frames", [])) != args.columns * args.rows:
        parser.error("timeline frame count must equal the grid cell count")
    durations = [int(frame["duration_ms"]) for frame in timeline["frames"]]

    cell_width = math.ceil(source.width / args.columns)
    cell_height = math.ceil(source.height / args.rows)
    common_scale = min(args.target_width / cell_width, args.target_height / cell_height)
    output_width = max(1, round(cell_width * common_scale))
    output_height = max(1, round(cell_height * common_scale))
    left = args.root_x - output_width // 2
    top = args.root_y - output_height
    if left < 0 or top < 0 or left + output_width > CELL[0] or top + output_height > CELL[1]:
        parser.error("shared root transform does not fit inside the 160x160 cell")

    master_dir = args.output_root / "master"
    frame_dir = master_dir / "frames"
    review_dir = args.output_root / "review"
    frame_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    frames: list[Image.Image] = []
    reports: list[dict[str, object]] = []
    total_fringe = 0
    total_debris = 0
    for index in range(args.columns * args.rows):
        column = index % args.columns
        row = index // args.columns
        bounds = (
            round(column * source.width / args.columns),
            round(row * source.height / args.rows),
            round((column + 1) * source.width / args.columns),
            round((row + 1) * source.height / args.rows),
        )
        actual_cell_width = bounds[2] - bounds[0]
        actual_cell_height = bounds[3] - bounds[1]
        cleaned, fringe_pixels, debris_pixels = clean_cell(source.crop(bounds))
        alpha_bbox = cleaned.getchannel("A").getbbox()
        if alpha_bbox is None:
            parser.error(f"cell {index} is empty after alpha cleanup")
        x0, y0, x1, y1 = alpha_bbox
        touches = {
            "left": x0 < 2,
            "top": y0 < 2,
            "right": x1 > actual_cell_width - 2,
            "bottom": y1 > actual_cell_height - 2,
        }
        normalized = cleaned.resize((output_width, output_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", CELL, (0, 0, 0, 0))
        canvas.alpha_composite(normalized, (left, top))
        canvas.save(frame_dir / f"se_{index:02}.png")
        frames.append(canvas)
        total_fringe += fringe_pixels
        total_debris += debris_pixels
        reports.append({
            "frame_index": index,
            "source_frame": timeline["frames"][index].get("source_frame"),
            "phase": timeline["frames"][index].get("phase"),
            "duration_ms": durations[index],
            "source_cell_xyxy": list(bounds),
            "source_alpha_bbox_xyxy": list(alpha_bbox),
            "source_alpha_touches_cell_edge": touches,
            "removed_bright_fringe_pixels": fringe_pixels,
            "removed_small_component_pixels": debris_pixels,
        })

    write_sheet(frames, master_dir / "basicattack-se-master-4x4.png", args.columns)
    write_sheet(frames, master_dir / "basicattack-se-master-16-strip.png", 1)
    write_contact(frames, review_dir / "basicattack-se-master-contact-4x4.png", args.columns)
    gif_duration = write_gif(frames, durations, review_dir / "basicattack-se-master-one-shot.gif", args.review_scale)
    provenance = {
        "status": "REVIEW_CANDIDATE_IMAGEGEN_FULL_FRAME_MASTER_NOT_RUNTIME_APPROVED",
        "source_sheet": str(args.sheet.resolve()),
        "source_sheet_sha256": sha256(args.sheet),
        "timeline": str(args.timeline.resolve()),
        "timeline_sha256": sha256(args.timeline),
        "grid": [args.columns, args.rows],
        "source_cell_px": [cell_width, cell_height],
        "normalization": {
            "runtime_cell_px": list(CELL),
            "shared_scale": common_scale,
            "content_px": [output_width, output_height],
            "root_px": [args.root_x, args.root_y],
            "cell_offset_px": [left, top],
            "cleanup": "remove alpha below 8, vivid red/magenta edge fringe and disconnected components under 12 pixels; no inpainting",
        },
        "playback": {
            "frame_count": len(frames),
            "source_duration_ms": sum(durations),
            "gif_duration_ms_with_final_recovery_hold": gif_duration,
            "final_recovery_hold_ms": max(600, durations[-1]),
            "gif_loop_extension": False,
            "gif_timing_quantization_ms": 10,
        },
        "frame_audit": reports,
        "summary": {
            "frames_touching_source_cell_edges": [item["frame_index"] for item in reports if any(item["source_alpha_touches_cell_edge"].values())],
            "removed_bright_fringe_pixels": total_fringe,
            "removed_small_component_pixels": total_debris,
        },
        "limitations": [
            "One direction and one action only.",
            "Generated cell poses are a visual trial and may not match the guide pose-for-pose.",
            "Same-frame cutouts and reconstruction comparison have not been completed.",
            "No game runtime preview or owner approval has been recorded.",
        ],
    }
    provenance_path = review_dir / "basicattack-se-master-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "frame_count": len(frames),
        "source_cell_px": [cell_width, cell_height],
        "normalized_content_px": [output_width, output_height],
        "source_cell_edge_touches": provenance["summary"]["frames_touching_source_cell_edges"],
        "removed_fringe_pixels": total_fringe,
        "removed_debris_pixels": total_debris,
        "source_duration_ms": sum(durations),
        "gif_duration_ms_with_recovery_hold": gif_duration,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
