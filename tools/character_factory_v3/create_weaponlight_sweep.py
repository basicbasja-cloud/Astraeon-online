#!/usr/bin/env python3
"""Build a phase-registered WeaponLight layer from one original sweep painting."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image


GRID = (4, 4)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_opacity_map(path: Path) -> list[float]:
    values = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(values, list)
        or len(values) != 16
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0.0 <= value <= 1.0
            for value in values
        )
    ):
        raise ValueError("frame opacity map must contain 16 numbers in [0, 1]")
    return [float(value) for value in values]


def read_transform_map(
    path: Path,
    offset_limit: float = 24,
) -> list[dict[str, float] | None]:
    values = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(values, list) or len(values) != 16:
        raise ValueError("frame transform map must contain 16 entries")
    normalized: list[dict[str, float] | None] = []
    for index, item in enumerate(values):
        if item is None:
            normalized.append(None)
            continue
        if not isinstance(item, dict):
            raise ValueError(f"frame transform {index} must be an object or null")
        required = {"width_scale", "angle_degrees", "offset_x", "offset_y"}
        if set(item) != required:
            raise ValueError(f"frame transform {index} must use exactly {sorted(required)}")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in item.values()):
            raise ValueError(f"frame transform {index} contains a non-number")
        if not 0.1 <= item["width_scale"] <= 1.5:
            raise ValueError(f"frame transform {index} width_scale must be in [0.1, 1.5]")
        if not -60 <= item["angle_degrees"] <= 60:
            raise ValueError(f"frame transform {index} angle_degrees must be in [-60, 60]")
        if (
            not -offset_limit <= item["offset_x"] <= offset_limit
            or not -offset_limit <= item["offset_y"] <= offset_limit
        ):
            raise ValueError(
                f"frame transform {index} offsets must be in "
                f"[-{offset_limit:g}, {offset_limit:g}]"
            )
        normalized.append({key: float(value) for key, value in item.items()})
    return normalized


def compose_inside_cell(
    source: Image.Image,
    bbox: tuple[int, int, int, int],
    transform: dict[str, float],
    base_width: int,
    thickness_scale_y: float,
    opacity: float,
    frame_opacity: float,
    cell_size: int,
) -> tuple[Image.Image, list[int]]:
    crop = source.crop(bbox)
    width = max(1, round(base_width * transform["width_scale"]))
    aspect = crop.height / crop.width
    height = max(1, round(width * aspect * thickness_scale_y))
    scaled = crop.resize((width, height), Image.Resampling.LANCZOS)
    rotated = scaled.rotate(
        transform["angle_degrees"],
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    center_x = round(cell_size / 2 + transform["offset_x"])
    center_y = round(cell_size * 0.54 + transform["offset_y"])
    left = center_x - rotated.width // 2
    top = center_y - rotated.height // 2
    canvas = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
    src_left = max(0, -left)
    src_top = max(0, -top)
    src_right = min(rotated.width, cell_size - left)
    src_bottom = min(rotated.height, cell_size - top)
    if src_right > src_left and src_bottom > src_top:
        visible = rotated.crop((src_left, src_top, src_right, src_bottom))
        canvas.alpha_composite(visible, (max(0, left), max(0, top)))

    alpha = canvas.getchannel("A").point(
        lambda value: 0 if value < 8 else round(value * opacity * frame_opacity)
    )
    canvas.putalpha(alpha.point(lambda value: 0 if value < 8 else value))
    visible_bbox = canvas.getchannel("A").point(lambda value: 255 if value >= 8 else 0).getbbox()
    if visible_bbox is None:
        raise ValueError("active trail frame became fully transparent")
    return canvas, list(visible_bbox)


def write_contact_sheet(frames: list[Image.Image], path: Path, cell_size: int) -> None:
    sheet = Image.new("RGBA", (cell_size * GRID[0], cell_size * GRID[1]), (235, 235, 235, 255))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % GRID[0]) * cell_size, (index // GRID[0]) * cell_size))
    sheet.convert("RGB").save(path)


def write_transparent_sheet(frames: list[Image.Image], path: Path, cell_size: int) -> None:
    sheet = Image.new("RGBA", (cell_size * GRID[0], cell_size * GRID[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % GRID[0]) * cell_size, (index // GRID[0]) * cell_size))
    sheet.save(path)


def write_vertical_strip(frames: list[Image.Image], path: Path, cell_size: int) -> None:
    strip = Image.new("RGBA", (cell_size, cell_size * len(frames)), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (0, index * cell_size))
    strip.save(path)


def write_gif(
    frames: list[Image.Image],
    durations: list[int],
    path: Path,
    scale: int,
    cell_size: int,
) -> int:
    background = (235, 235, 235, 255)
    canvases = []
    for frame in frames:
        canvas = Image.new("RGBA", (cell_size, cell_size), background)
        canvas.alpha_composite(frame)
        if scale != 1:
            canvas = canvas.resize((cell_size * scale, cell_size * scale), Image.Resampling.LANCZOS)
        canvases.append(canvas.convert("RGB"))

    palette_source = Image.new("RGB", (canvases[0].width, canvases[0].height * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * canvas.height))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in canvases]

    held = list(durations)
    held[-1] = max(held[-1], 600)
    target_units = (sum(held) + 5) // 10
    units = [duration // 10 for duration in held]
    remainder_units = target_units - sum(units)
    order = sorted(range(len(held)), key=lambda index: (-(held[index] % 10), index))
    for index in order[:remainder_units]:
        units[index] += 1
    encoded = [unit * 10 for unit in units]
    indexed[0].save(
        path,
        save_all=True,
        append_images=indexed[1:],
        duration=encoded,
        disposal=2,
        optimize=False,
    )
    return sum(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-image", type=Path, required=True, help="Single RGBA sweep source image")
    parser.add_argument("--frames-dir", type=Path, required=True, help="Directory with se_00.png through se_15.png")
    parser.add_argument("--timeline", type=Path, required=True, help="16-frame timing JSON")
    parser.add_argument("--frame-opacity-map", type=Path, required=True, help="16 per-frame trail opacity multipliers")
    parser.add_argument("--frame-transform-map", type=Path, required=True, help="16 per-frame trail transforms")
    parser.add_argument("--layers-dir", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--base-width", type=int, default=120)
    parser.add_argument("--thickness-scale-y", type=float, default=1.35)
    parser.add_argument("--opacity", type=float, default=0.94)
    parser.add_argument("--offset-y", type=int, default=0)
    parser.add_argument("--scale", type=int, default=3, help="Review GIF integer scale")
    parser.add_argument("--cell-size", type=int, default=160, help="Square frame canvas in pixels")
    args = parser.parse_args()
    if (
        args.base_width < 1
        or not 0.5 <= args.thickness_scale_y <= 2.0
        or not 0.0 < args.opacity <= 1.0
        or args.scale < 1
        or args.cell_size < 32
    ):
        parser.error("invalid width, thickness, opacity or review scale")

    source = Image.open(args.sweep_image).convert("RGBA")
    source_alpha = source.getchannel("A")
    clean_alpha = source_alpha.point(lambda value: 255 if value >= 8 else 0)
    bbox = clean_alpha.getbbox()
    if bbox is None:
        parser.error("source sweep contains no visible alpha pixels")
    source.putalpha(source_alpha.point(lambda value: 0 if value < 8 else value))

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    timeline_frames = timeline.get("frames", [])
    if len(timeline_frames) != 16:
        parser.error(f"timeline must contain exactly 16 frames; got {len(timeline_frames)}")
    durations = [int(frame["duration_ms"]) for frame in timeline_frames]
    opacity_map = read_opacity_map(args.frame_opacity_map)
    transform_map = read_transform_map(
        args.frame_transform_map,
        offset_limit=max(24, args.cell_size * 0.4),
    )
    if any((opacity_map[index] == 0) != (transform_map[index] is None) for index in range(16)):
        parser.error("opacity and transform maps must mark the same active frames")

    args.layers_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = args.layers_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    args.review_dir.mkdir(parents=True, exist_ok=True)

    trails: list[Image.Image] = []
    records: list[dict[str, Any]] = []
    for index, transform in enumerate(transform_map):
        frame = Image.new("RGBA", (args.cell_size, args.cell_size), (0, 0, 0, 0))
        visible_bbox: list[int] = []
        if transform is not None:
            adjusted = dict(transform)
            adjusted["offset_y"] += args.offset_y
            frame, visible_bbox = compose_inside_cell(
                source,
                bbox,
                adjusted,
                args.base_width,
                args.thickness_scale_y,
                args.opacity,
                opacity_map[index],
                args.cell_size,
            )
            margin = max(3, round(args.cell_size * 3 / 160))
            if (
                visible_bbox[0] < margin
                or visible_bbox[1] < margin
                or visible_bbox[2] > args.cell_size - margin
                or visible_bbox[3] > args.cell_size - margin
            ):
                raise ValueError(f"frame {index} trail touches the 3px safety boundary: {visible_bbox}")
        frame.save(frames_dir / f"weaponlight_se_{index:02}.png")
        trails.append(frame)
        records.append({
            "frame_index": index,
            "phase": timeline_frames[index]["phase"],
            "duration_ms": durations[index],
            "active": transform is not None,
            "opacity_multiplier": opacity_map[index],
            "transform": transform,
            "alpha_bbox_xyxy": visible_bbox,
        })

    write_transparent_sheet(trails, args.layers_dir / "weaponlight-se-4x4.png", args.cell_size)
    write_vertical_strip(trails, args.layers_dir / "weaponlight-se-16.png", args.cell_size)

    poses: list[Image.Image] = []
    for index in range(16):
        pose_path = args.frames_dir / f"se_{index:02}.png"
        if not pose_path.exists():
            parser.error(f"missing character frame: {pose_path}")
        pose = Image.open(pose_path).convert("RGBA")
        if pose.size != (args.cell_size, args.cell_size):
            parser.error(
                f"character frames must be {args.cell_size}x{args.cell_size}; "
                f"{pose_path} is {pose.size}"
            )
        poses.append(pose)

    behind: list[Image.Image] = []
    over: list[Image.Image] = []
    for pose, trail in zip(poses, trails):
        behind_frame = trail.copy()
        behind_frame.alpha_composite(pose)
        behind.append(behind_frame)
        over_frame = pose.copy()
        over_frame.alpha_composite(trail)
        over.append(over_frame)

    write_contact_sheet(behind, args.review_dir / "weaponlight-behind-contact-4x4.png", args.cell_size)
    write_contact_sheet(over, args.review_dir / "weaponlight-over-contact-4x4.png", args.cell_size)
    behind_duration = write_gif(
        behind,
        durations,
        args.review_dir / "basicattack-se-weaponlight-behind-one-shot.gif",
        args.scale,
        args.cell_size,
    )
    over_duration = write_gif(
        over,
        durations,
        args.review_dir / "basicattack-se-weaponlight-one-shot.gif",
        args.scale,
        args.cell_size,
    )
    if behind_duration != over_duration:
        raise AssertionError("over/behind GIF timing differs")

    provenance = {
        "status": "REVIEW_ONLY_SE_WEAPONLIGHT_NOT_RUNTIME_APPROVED",
        "source_sweep_image": str(args.sweep_image.resolve()),
        "source_sweep_sha256": sha256(args.sweep_image),
        "source_alpha_threshold": 8,
        "source_alpha_bbox_xyxy": list(bbox),
        "timeline": str(args.timeline.resolve()),
        "timeline_sha256": sha256(args.timeline),
        "opacity_map": str(args.frame_opacity_map.resolve()),
        "opacity_map_sha256": sha256(args.frame_opacity_map),
        "transform_map": str(args.frame_transform_map.resolve()),
        "transform_map_sha256": sha256(args.frame_transform_map),
        "normalization": {
            "canvas_px": [args.cell_size, args.cell_size],
            "base_visible_width_px": args.base_width,
            "vertical_thickness_scale": args.thickness_scale_y,
            "base_opacity_multiplier": args.opacity,
            "global_offset_y_px": args.offset_y,
            "per_frame_alpha_threshold": 8,
            "safety_margin_px": 3,
            "colors": "original plum-gray, lavender-silver and warm-ivory from source image",
            "registration": "single source glyph transformed on the action timeline; character frames and root are unchanged",
        },
        "playback": {
            "frame_count": 16,
            "duration_source_ms": sum(durations),
            "gif_duration_ms_with_recovery_hold": over_duration,
            "gif_loop_extension": False,
            "final_recovery_hold_ms": max(600, durations[-1]),
            "gif_timing_quantization_ms": 10,
            "contact_phase": timeline.get("semantic_phases", {}).get("contact"),
        },
        "frames": records,
        "outputs": {
            "transparent_sheet": str((args.layers_dir / "weaponlight-se-4x4.png").resolve()),
            "vertical_strip": str((args.layers_dir / "weaponlight-se-16.png").resolve()),
            "over_contact_sheet": str((args.review_dir / "weaponlight-over-contact-4x4.png").resolve()),
            "behind_contact_sheet": str((args.review_dir / "weaponlight-behind-contact-4x4.png").resolve()),
            "over_one_shot_gif": str((args.review_dir / "basicattack-se-weaponlight-one-shot.gif").resolve()),
            "behind_one_shot_gif": str((args.review_dir / "basicattack-se-weaponlight-behind-one-shot.gif").resolve()),
        },
        "limitations": [
            "Single SE direction only.",
            "The underlying painted character master still has red fringe and clipped blade pixels.",
            "Trail art is a review prototype and has not been admitted to runtime.",
            "Motion curves, character poses and frame durations are unchanged.",
        ],
    }
    provenance_path = args.review_dir / "weaponlight-sweep-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "frame_count": len(trails),
        "active_frames_1_based": [r["frame_index"] + 1 for r in records if r["active"]],
        "active_frame_bounds": [r["alpha_bbox_xyxy"] for r in records if r["active"]],
        "source_duration_ms": sum(durations),
        "gif_duration_ms_with_recovery_hold": over_duration,
        "provenance_sha256": sha256(provenance_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
