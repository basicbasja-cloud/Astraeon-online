#!/usr/bin/env python3
"""Clean and normalize a 4x4 single-facing generated animation prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

import numpy as np
from PIL import Image
from scipy import ndimage


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def remove_checkerboard_background(cell: Image.Image) -> tuple[Image.Image, int]:
    rgb = np.asarray(cell.convert("RGB"), dtype=np.uint8)
    maximum = rgb.max(axis=2).astype(np.int16)
    minimum = rgb.min(axis=2).astype(np.int16)
    # The source's faux transparency grid is neutral gray near #d8d8d8/#fcfcfc.
    candidate = (maximum - minimum <= 16) & (minimum >= 180)
    edge = np.zeros(candidate.shape, dtype=bool)
    edge[0, :] = candidate[0, :]
    edge[-1, :] = candidate[-1, :]
    edge[:, 0] = candidate[:, 0]
    edge[:, -1] = candidate[:, -1]
    background = ndimage.binary_propagation(edge, mask=candidate)
    alpha = np.where(background, 0, 255).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))
    return Image.fromarray(rgba, "RGBA"), int(background.sum())


def find_baseline_and_root_x(cell: Image.Image) -> tuple[int, float, int, tuple[int, int, int, int]]:
    # Ignore very faint matte pixels when measuring feet and the character box.
    alpha = np.asarray(cell.getchannel("A"), dtype=np.uint8) > 64
    height, width = alpha.shape
    row_counts = alpha.sum(axis=1)
    baseline_rows = np.flatnonzero((np.arange(height) >= height * 0.62) & (row_counts >= 6))
    if not len(baseline_rows):
        raise ValueError("Could not locate a boot baseline in one prototype frame")
    baseline = int(baseline_rows[-1] + 1)

    x0, x1 = int(width * 0.18), int(width * 0.82)
    body_counts = alpha[:, x0:x1].sum(axis=1)
    body_rows = np.flatnonzero((np.arange(height) < baseline) & (body_counts >= 4))
    if not len(body_rows):
        raise ValueError("Could not locate the character body in one prototype frame")
    top = int(body_rows[0])
    body_height = baseline - top
    foot_band = alpha[max(0, baseline - 10):baseline, :]
    foot_x = np.nonzero(foot_band)[1]
    if not len(foot_x):
        raise ValueError("Could not locate boot pixels in one prototype frame")
    root_x = float(np.median(foot_x))
    bounds = cell.getchannel("A").getbbox()
    assert bounds is not None
    return body_height, root_x, baseline, bounds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--direction", default="SE")
    parser.add_argument("--target-height", type=int, default=112)
    parser.add_argument("--root", type=int, nargs=2, default=(80, 132))
    parser.add_argument("--lock-recovery-to-first", action="store_true",
                        help="Use the normalized first guard pose as frame 16 for a seamless review loop")
    args = parser.parse_args()

    source_path = args.input.resolve()
    timeline_path = args.timeline.resolve()
    output_root = args.output_root.resolve()
    opened_source = Image.open(source_path).convert("RGBA")
    source_has_alpha = opened_source.getchannel("A").getextrema()[0] < 255
    source = opened_source if source_has_alpha else opened_source.convert("RGB")
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    frames = timeline.get("frames", [])
    if len(frames) != 16 or int(timeline.get("frame_count", 0)) != 16:
        raise ValueError("Single-direction prototype requires exactly 16 timeline frames")
    if timeline.get("action") != "BasicAttack" or timeline.get("loop"):
        raise ValueError("This prototype is for one-shot BasicAttack only")

    source_width, source_height = source.size
    x_edges = [round(index * source_width / 4) for index in range(5)]
    y_edges = [round(index * source_height / 4) for index in range(5)]
    cells: list[Image.Image] = []
    removed_background: list[int] = []
    source_boxes: list[tuple[int, int, int, int]] = []
    measurements: list[tuple[int, float, tuple[int, int, int, int]]] = []
    for index in range(16):
        row, col = divmod(index, 4)
        source_cell = source.crop((x_edges[col], y_edges[row], x_edges[col + 1], y_edges[row + 1]))
        if source_has_alpha:
            cell, removed = source_cell.convert("RGBA"), 0
        else:
            cell, removed = remove_checkerboard_background(source_cell)
        cells.append(cell)
        removed_background.append(removed)
        source_boxes.append((x_edges[col], y_edges[row], x_edges[col + 1], y_edges[row + 1]))
        measurements.append(find_baseline_and_root_x(cell))

    source_body_height = median(item[0] for item in measurements)
    scale = args.target_height / source_body_height
    normalized_frames: list[Image.Image] = []
    output_root.mkdir(parents=True, exist_ok=True)
    frame_root = output_root / "frames"
    frame_root.mkdir(parents=True, exist_ok=True)
    normalized_sheet = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    vertical_sheet = Image.new("RGBA", (160, 2560), (0, 0, 0, 0))
    frame_records = []
    for index, (cell, timing, measurement, source_box) in enumerate(
            zip(cells, frames, measurements, source_boxes, strict=True)):
        source_body_height_i, measured_foot_center_x, baseline, source_alpha_bounds = measurement
        # The generated cells are centered on the fixed motion-guide root. Foot
        # medians jump sideways on lunges and would make the character slide.
        root_x = cell.width / 2
        resized_size = (max(1, round(cell.width * scale)), max(1, round(cell.height * scale)))
        resized = cell.convert("RGBa").resize(resized_size, Image.Resampling.LANCZOS).convert("RGBA")
        left = round(args.root[0] - root_x * scale)
        top = round(args.root[1] - baseline * scale)
        canvas = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        canvas.alpha_composite(resized, (left, top))
        recovery_locked = args.lock_recovery_to_first and index == 15
        if recovery_locked:
            # The BasicAttack remains a one-shot in the runtime. This review GIF
            # uses its first guard pose as the final recovery pose so the looped
            # comparison has an exact, inspectable seam.
            canvas = normalized_frames[0].copy()
        normalized_frames.append(canvas)
        frame_path = frame_root / f"{args.direction.lower()}_{index:02d}.png"
        canvas.save(frame_path)
        vertical_sheet.alpha_composite(canvas, (0, index * 160))
        normalized_sheet.alpha_composite(canvas, ((index % 4) * 160, (index // 4) * 160))
        frame_records.append({
            "frame_index": index,
            "phase": float(timing["phase"]),
            "duration_ms": int(timing["duration_ms"]),
            "source_frame_box": list(source_box),
            "source_alpha_bbox": list(source_alpha_bounds),
            "source_body_height_px": source_body_height_i,
            "source_root_x_px": round(root_x, 3),
            "measured_foot_center_x_px": round(measured_foot_center_x, 3),
            "source_boot_baseline_y_px": baseline,
            "normalized_translation_px": [left, top],
            "recovery_locked_to_first_frame": recovery_locked,
        })

    vertical_path = output_root / f"basicattack-{args.direction.lower()}-master-16.png"
    contact_path = output_root / f"basicattack-{args.direction.lower()}-contact-4x4.png"
    gif_path = output_root / f"basicattack-{args.direction.lower()}-16.gif"
    vertical_sheet.save(vertical_path)
    normalized_sheet.save(contact_path)

    gif_frames = []
    for frame in normalized_frames:
        # A light neutral preview exposes any red matte left around transparent edges.
        preview = Image.new("RGBA", frame.size, (232, 232, 232, 255))
        preview.alpha_composite(frame)
        gif_frames.append(preview.convert("P", palette=Image.Palette.ADAPTIVE, colors=255))
    durations = [int(item["duration_ms"]) for item in frames]
    gif_durations = []
    elapsed, boundary = 0, 0
    for duration in durations:
        elapsed += duration
        next_boundary = ((elapsed + 5) // 10) * 10
        gif_durations.append(max(10, next_boundary - boundary))
        boundary = next_boundary
    gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:],
                       duration=gif_durations, loop=0, optimize=False, disposal=2)

    provenance = {
        "status": "SE_SINGLE_DIRECTION_PROTOTYPE_REQUIRES_VISUAL_AND_LAYER_REVIEW",
        "source_image": str(source_path),
        "source_image_sha256": sha256(source_path),
        "timeline": str(timeline_path),
        "timeline_sha256": sha256(timeline_path),
        "source_grid": {"columns": 4, "rows": 4, "size_px": [source_width, source_height]},
        "source_transparency_recovery": {
            "method": ("preserved source alpha" if source_has_alpha else
                       "per-cell edge-connected neutral gray removal for the baked checkerboard preview"),
            "removed_pixels_per_frame": removed_background,
        },
        "direction": args.direction,
        "frame_count": 16,
        "loop": False,
        "gif_preview_loop": True,
        "gif_preview_recovery_lock": args.lock_recovery_to_first,
        "source_median_body_height_px": source_body_height,
        "target_body_height_px": args.target_height,
        "shared_scale": round(scale, 6),
        "root": list(args.root),
        "root_alignment_method": "fixed center of each source cell; foot median is diagnostic only",
        "gif_timeline_duration_ms": sum(durations),
        "gif_encoded_duration_ms": sum(gif_durations),
        "gif_timing_quantization_ms": 10,
        "files": {
            "vertical_master": str(vertical_path),
            "contact_sheet": str(contact_path),
            "gif": str(gif_path),
        },
        "frames": frame_records,
        "limitations": [
            "Single SE facing only; not a complete eight-direction runtime master.",
            "Full-character art only; modular layer masks have not been created.",
            "Background recovery uses a deterministic neutral checkerboard mask and needs edge review.",
        ],
    }
    provenance_path = output_root / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"master": str(vertical_path), "contact_sheet": str(contact_path),
                      "gif": str(gif_path), "provenance": str(provenance_path)}))


if __name__ == "__main__":
    main()
