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


DEFAULT_CELL = (160, 160)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_cell(cell: Image.Image, debris_limit: int = 12) -> tuple[Image.Image, int, int]:
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
    rgba[fringe, :3] = 0

    faint = rgba[:, :, 3] < 8
    rgba[faint] = 0
    components, count = ndimage.label(rgba[:, :, 3] > 0, structure=np.ones((3, 3), dtype=np.uint8))
    sizes = np.bincount(components.ravel())
    small = sizes < debris_limit
    small[0] = False
    debris = small[components]
    debris_pixels = int(debris.sum())
    rgba[debris] = 0
    return Image.fromarray(rgba, "RGBA"), fringe_pixels, debris_pixels


def resize_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resample premultiplied RGBA to prevent hidden matte colors bleeding into edges."""
    return image.convert("RGBa").resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def find_foot_baseline(cell: Image.Image) -> tuple[int, str]:
    """Find the boot sole line, including wide lunges where neither boot is centered."""
    rgba = np.asarray(cell.convert("RGBA"), dtype=np.uint8)
    alpha = rgba[:, :, 3] > 64
    height, width = alpha.shape

    # Full-body paintovers often place both boots outside the center band during a
    # wide lunge. In that case the center-band fallback can mistake a knee or a
    # sword guard for the floor. The Swordsman's dark warm-brown footwear gives us
    # a stable contact cue without letting the gold cape or steel blade set the root.
    red, green, blue = (rgba[:, :, channel].astype(np.int16) for channel in range(3))
    footwear = (
        alpha
        & (red >= 25)
        & (red < 190)
        & (green > 8)
        & (green < 135)
        & (blue < 120)
        & (red >= green)
        & (red > blue * 1.1)
    )
    footwear[: round(height * 0.62)] = False
    footwear_rows = footwear.sum(axis=1)
    footwear_contacts = np.flatnonzero(footwear_rows >= 3)
    if len(footwear_contacts):
        return int(footwear_contacts[-1]), "warm_brown_footwear_band"

    # Fall back to a lower-center silhouette band for characters without warm
    # brown boots, still avoiding isolated weapon tips outside the character.
    x0, x1 = round(width * 0.30), round(width * 0.70)
    y0 = round(height * 0.62)
    rows = alpha[y0:, x0:x1].sum(axis=1)
    grounded = np.flatnonzero(rows >= 2)
    if len(grounded):
        return y0 + int(grounded[-1]) + 1, "lower_center_boot_band"
    bounds = cell.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Cannot find a boot baseline in an empty sprite cell")
    return bounds[3], "alpha_bbox_fallback"


def write_sheet(frames: list[Image.Image], path: Path, columns: int, cell: tuple[int, int]) -> None:
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell[0], rows * cell[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % columns) * cell[0], (index // columns) * cell[1]))
    sheet.save(path)


def write_contact(frames: list[Image.Image], path: Path, columns: int, cell: tuple[int, int]) -> None:
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell[0], rows * cell[1]), (235, 235, 235, 255))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % columns) * cell[0], (index // columns) * cell[1]))
    sheet.convert("RGB").save(path)


def write_gif(frames: list[Image.Image], durations: list[int], path: Path, scale: int,
              cell: tuple[int, int]) -> int:
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", cell, (235, 235, 235, 255))
        canvas.alpha_composite(frame)
        if scale != 1:
            canvas = canvas.resize((cell[0] * scale, cell[1] * scale), Image.Resampling.LANCZOS)
        canvases.append(canvas.convert("RGB"))

    palette_source = Image.new("RGB", (canvases[0].width, canvases[0].height * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * canvas.height))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in canvases]

    held = list(durations)
    held[-1] = max(held[-1], 300)
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
    parser.add_argument("--cell-size", type=int, default=DEFAULT_CELL[0],
                        help="Square output cell in pixels; use 320 for the 2x painted master")
    parser.add_argument("--target-width", type=int, default=150,
                        help="Maximum character/effect width in pixels when root-alignment is enabled")
    parser.add_argument("--target-height", type=int, default=112,
                        help="Maximum character/effect height in pixels when root-alignment is enabled")
    parser.add_argument("--root-x", type=int, default=80)
    parser.add_argument("--root-y", type=int, default=132)
    parser.add_argument("--review-scale", type=int, default=3)
    parser.add_argument("--align-feet-to-root", action="store_true",
                        help="Use one shared scale and align each frame's lower boot baseline to the root")
    parser.add_argument("--debris-limit", type=int, default=12,
                        help="Remove disconnected alpha components smaller than this many source pixels")
    args = parser.parse_args()
    if min(args.columns, args.rows, args.cell_size, args.target_width, args.target_height,
           args.review_scale, args.debris_limit) < 1:
        parser.error("grid, target dimensions and review scale must be positive")
    cell = (args.cell_size, args.cell_size)

    source = Image.open(args.sheet).convert("RGBA")
    if source.width < args.columns or source.height < args.rows:
        parser.error(f"sheet size {source.size} is too small for {args.columns}x{args.rows}")
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    if len(timeline.get("frames", [])) != args.columns * args.rows:
        parser.error("timeline frame count must equal the grid cell count")
    durations = [int(frame["duration_ms"]) for frame in timeline["frames"]]

    x_edges = [round(index * source.width / args.columns) for index in range(args.columns + 1)]
    y_edges = [round(index * source.height / args.rows) for index in range(args.rows + 1)]
    cell_width = max(x_edges[index + 1] - x_edges[index] for index in range(args.columns))
    cell_height = max(y_edges[index + 1] - y_edges[index] for index in range(args.rows))
    prepared: list[dict[str, object]] = []
    for index in range(args.columns * args.rows):
        column, row = index % args.columns, index // args.columns
        bounds = (x_edges[column], y_edges[row], x_edges[column + 1], y_edges[row + 1])
        crop = source.crop(bounds)
        cleaned, fringe_pixels, debris_pixels = clean_cell(crop, args.debris_limit)
        alpha_bbox = cleaned.getchannel("A").getbbox()
        if alpha_bbox is None:
            parser.error(f"cell {index} is empty after alpha cleanup")
        baseline, baseline_method = find_foot_baseline(cleaned) if args.align_feet_to_root else (bounds[3] - bounds[1], "cell_bottom")
        prepared.append({
            "cleaned": cleaned, "bbox": alpha_bbox, "source_bounds": bounds,
            "fringe_pixels": fringe_pixels, "debris_pixels": debris_pixels,
            "baseline": baseline, "baseline_method": baseline_method,
        })

    if args.align_feet_to_root:
        margin = 4
        left_extent = right_extent = up_extent = down_extent = 1.0
        for item in prepared:
            x0, y0, x1, y1 = item["bbox"]
            source_bounds = item["source_bounds"]
            source_center_x = (source_bounds[2] - source_bounds[0]) / 2
            baseline = int(item["baseline"])
            left_extent = max(left_extent, source_center_x - x0)
            right_extent = max(right_extent, x1 - source_center_x)
            up_extent = max(up_extent, baseline - y0)
            down_extent = max(down_extent, y1 - baseline)
        max_content_width = left_extent + right_extent
        max_content_height = up_extent + down_extent
        # The input cells contain generous transparent padding, so target size
        # must be measured against the shared character/effect bounds, not the
        # entire 512px cell. Otherwise a 224px tall design is reduced to ~120px.
        scale_limits = [
            args.target_width / (left_extent + right_extent),
            args.target_height / (up_extent + down_extent),
            (args.root_x - margin) / left_extent,
            (cell[0] - args.root_x - margin) / right_extent,
            (args.root_y - margin) / up_extent,
            (cell[1] - args.root_y - margin) / down_extent,
        ]
    else:
        scale_limits = [args.target_width / cell_width, args.target_height / cell_height]
    common_scale = min(scale_limits)
    if args.align_feet_to_root:
        output_width = max(1, round(max_content_width * common_scale))
        output_height = max(1, round(max_content_height * common_scale))
    else:
        output_width = max(1, round(cell_width * common_scale))
        output_height = max(1, round(cell_height * common_scale))
    legacy_left = args.root_x - output_width // 2
    legacy_top = args.root_y - output_height
    if not args.align_feet_to_root and (legacy_left < 0 or legacy_top < 0 or
            legacy_left + output_width > cell[0] or legacy_top + output_height > cell[1]):
        parser.error(f"shared root transform does not fit inside the {cell[0]}x{cell[1]} cell")

    master_dir = args.output_root / "master"
    frame_dir = master_dir / "frames"
    review_dir = args.output_root / "review"
    frame_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    frames: list[Image.Image] = []
    reports: list[dict[str, object]] = []
    total_fringe = 0
    total_debris = 0
    output_anchor_errors: list[int] = []
    for index, item in enumerate(prepared):
        bounds = item["source_bounds"]
        actual_cell_width = bounds[2] - bounds[0]
        actual_cell_height = bounds[3] - bounds[1]
        cleaned = item["cleaned"]
        fringe_pixels = int(item["fringe_pixels"])
        debris_pixels = int(item["debris_pixels"])
        alpha_bbox = cleaned.getchannel("A").getbbox()
        assert alpha_bbox is not None
        x0, y0, x1, y1 = alpha_bbox
        touches = {
            "left": x0 < 2,
            "top": y0 < 2,
            "right": x1 > actual_cell_width - 2,
            "bottom": y1 > actual_cell_height - 2,
        }
        canvas = Image.new("RGBA", cell, (0, 0, 0, 0))
        if args.align_feet_to_root:
            baseline = int(item["baseline"])
            source_center_x = actual_cell_width / 2
            tile = cleaned.crop(alpha_bbox)
            tile_size = (max(1, round(tile.width * common_scale)), max(1, round(tile.height * common_scale)))
            normalized = resize_rgba(tile, tile_size)
            left = round(args.root_x + (x0 - source_center_x) * common_scale)
            top = round(args.root_y + (y0 - baseline) * common_scale)
            if left < 0 or top < 0 or left + tile_size[0] > cell[0] or top + tile_size[1] > cell[1]:
                parser.error(f"frame {index} does not fit after shared foot-root alignment")
            canvas.alpha_composite(normalized, (left, top))
            # Resampling can move the last visible boot pixel by one row. Correct
            # that after scaling so every frame lands on the same runtime root.
            rendered_baseline, _ = find_foot_baseline(canvas)
            root_correction = args.root_y - rendered_baseline
            if root_correction:
                corrected = Image.new("RGBA", cell, (0, 0, 0, 0))
                corrected.alpha_composite(canvas, (0, root_correction))
                canvas = corrected
            final_baseline, final_method = find_foot_baseline(canvas)
            if final_baseline != args.root_y:
                parser.error(
                    f"frame {index} foot root landed at y={final_baseline}; expected {args.root_y}"
                )
            output_anchor_errors.append(final_baseline - args.root_y)
        else:
            normalized = resize_rgba(cleaned, (output_width, output_height))
            left, top = legacy_left, legacy_top
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
            "source_foot_baseline_y_px": int(item["baseline"]),
            "source_foot_baseline_method": str(item["baseline_method"]),
            "output_foot_baseline_y_px": final_baseline if args.align_feet_to_root else None,
            "output_foot_baseline_method": final_method if args.align_feet_to_root else None,
            "output_root_correction_px": root_correction if args.align_feet_to_root else None,
            "removed_bright_fringe_pixels": fringe_pixels,
            "removed_small_component_pixels": debris_pixels,
        })

    write_sheet(frames, master_dir / "basicattack-se-master-4x4.png", args.columns, cell)
    write_sheet(frames, master_dir / "basicattack-se-master-16-strip.png", 1, cell)
    write_contact(frames, review_dir / "basicattack-se-master-contact-4x4.png", args.columns, cell)
    gif_duration = write_gif(frames, durations, review_dir / "basicattack-se-master-one-shot.gif", args.review_scale, cell)
    provenance = {
        "status": "REVIEW_CANDIDATE_IMAGEGEN_FULL_FRAME_MASTER_NOT_RUNTIME_APPROVED",
        "source_sheet": str(args.sheet.resolve()),
        "source_sheet_sha256": sha256(args.sheet),
        "timeline": str(args.timeline.resolve()),
        "timeline_sha256": sha256(args.timeline),
        "grid": [args.columns, args.rows],
        "source_cell_px": [cell_width, cell_height],
        "normalization": {
            "authoring_cell_px": list(cell),
            "shared_scale": common_scale,
            "content_px": [output_width, output_height],
            "root_px": [args.root_x, args.root_y],
            "cell_offset_px": [legacy_left, legacy_top] if not args.align_feet_to_root else None,
            "root_alignment_method": "shared cell-center x and exact post-resize footwear baseline y" if args.align_feet_to_root else "shared center and source-cell bottom",
            "cleanup": f"remove alpha below 8, vivid red/magenta edge fringe and disconnected components under {args.debris_limit} source pixels; premultiplied-alpha resize; no inpainting",
        },
        "playback": {
            "frame_count": len(frames),
            "source_duration_ms": sum(durations),
            "gif_duration_ms_with_final_recovery_hold": gif_duration,
            "final_recovery_hold_ms": max(300, durations[-1]),
            "gif_loop_extension": False,
            "gif_timing_quantization_ms": 10,
        },
        "frame_audit": reports,
        "summary": {
            "frames_touching_source_cell_edges": [item["frame_index"] for item in reports if any(item["source_alpha_touches_cell_edge"].values())],
            "root_baseline_y_px": args.root_y if args.align_feet_to_root else None,
            "max_output_root_baseline_error_px": max((abs(value) for value in output_anchor_errors), default=None),
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
