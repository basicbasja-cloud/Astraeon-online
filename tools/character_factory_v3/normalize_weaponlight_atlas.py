#!/usr/bin/env python3
"""Normalize an effect-only 4x4 atlas into frame-registered WeaponLight assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


COLOR_RAMP = [
    [0, [57, 49, 70]],       # plum-shadow outer edge
    [72, [101, 89, 118]],    # muted violet-gray
    [138, [157, 145, 175]],  # lavender silver
    [196, [216, 208, 222]],  # pale silver highlight
    [235, [248, 242, 229]],  # warm ivory edge
    [255, [255, 248, 232]],
]


def colorize_luminance(gray: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image]:
    channels: list[Image.Image] = []
    for channel in range(3):
        lut: list[int] = []
        for value in range(256):
            for index in range(len(COLOR_RAMP) - 1):
                low_value, low_rgb = COLOR_RAMP[index]
                high_value, high_rgb = COLOR_RAMP[index + 1]
                if value <= high_value:
                    ratio = (value - low_value) / (high_value - low_value)
                    lut.append(round(low_rgb[channel] + (high_rgb[channel] - low_rgb[channel]) * ratio))
                    break
            else:
                lut.append(COLOR_RAMP[-1][1][channel])
        channels.append(gray.point(lut))
    return channels[0], channels[1], channels[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_contact_sheet(frames: list[Image.Image], path: Path, background: tuple[int, int, int, int]) -> None:
    sheet = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        cell = Image.new("RGBA", (160, 160), background)
        cell.alpha_composite(frame)
        sheet.alpha_composite(cell, ((index % 4) * 160, (index // 4) * 160))
    sheet.convert("RGB").save(path)


def write_strip(frames: list[Image.Image], path: Path) -> None:
    strip = Image.new("RGBA", (160, 2560), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (0, index * 160))
    strip.save(path)


def write_transparent_contact_sheet(frames: list[Image.Image], path: Path) -> None:
    sheet = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, ((index % 4) * 160, (index // 4) * 160))
    sheet.save(path)


def write_gif(frames: list[Image.Image], durations: list[int], path: Path, scale: int) -> int:
    background = (235, 235, 235, 255)
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (160, 160), background)
        canvas.alpha_composite(frame)
        if scale != 1:
            canvas = canvas.resize((160 * scale, 160 * scale), Image.Resampling.LANCZOS)
        canvases.append(canvas.convert("RGB"))

    # A shared palette avoids color flicker between adjacent frames.
    palette_source = Image.new("RGB", (canvases[0].width, canvases[0].height * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * canvas.height))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in canvases]

    encoded_durations = list(durations)
    encoded_durations[-1] = max(encoded_durations[-1], 600)  # hold the recovery pose for review
    target_units = (sum(encoded_durations) + 5) // 10
    units = [duration // 10 for duration in encoded_durations]
    remaining_units = target_units - sum(units)
    remainder_order = sorted(
        range(len(encoded_durations)),
        key=lambda index: (-(encoded_durations[index] % 10), index),
    )
    for index in remainder_order[:remaining_units]:
        units[index] += 1
    encoded_durations = [unit * 10 for unit in units]
    indexed[0].save(
        path,
        save_all=True,
        append_images=indexed[1:],
        duration=encoded_durations,
        disposal=2,
        optimize=False,
    )
    return sum(encoded_durations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, required=True, help="Source RGBA 4x4 WeaponLight atlas")
    parser.add_argument("--frames-dir", type=Path, required=True, help="Directory with se_00.png through se_15.png")
    parser.add_argument("--timeline", type=Path, required=True, help="16-frame timing JSON")
    parser.add_argument("--frame-map", type=Path, required=True, help="JSON list mapping 16 output frames to 4x4 source cells; null means no trail")
    parser.add_argument("--layers-dir", type=Path, required=True, help="Output WeaponLight layer directory")
    parser.add_argument("--review-dir", type=Path, required=True, help="Output review artifact directory")
    parser.add_argument("--opacity", type=float, default=0.86, help="Trail opacity multiplier (default: 0.86)")
    parser.add_argument("--scale", type=int, default=3, help="GIF preview scale (default: 3)")
    parser.add_argument("--offset-x", type=int, default=0, help="Global trail layer offset in pixels (default: 0)")
    parser.add_argument("--offset-y", type=int, default=-20, help="Global trail layer offset in pixels (default: -20)")
    args = parser.parse_args()

    if not 0.0 < args.opacity <= 1.0:
        parser.error("--opacity must be in (0, 1]")
    if args.scale < 1:
        parser.error("--scale must be at least 1")

    atlas = Image.open(args.atlas).convert("RGBA")
    width, height = atlas.size
    if width < 4 or height < 4 or abs(width - height) > 1:
        parser.error(f"atlas must be square and at least 4px per side; got {atlas.size}")

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    timeline_frames = timeline.get("frames", [])
    if len(timeline_frames) != 16:
        parser.error(f"timeline must contain exactly 16 frames; got {len(timeline_frames)}")
    durations = [int(frame["duration_ms"]) for frame in timeline_frames]
    frame_map = json.loads(args.frame_map.read_text(encoding="utf-8"))
    if not isinstance(frame_map, list) or len(frame_map) != 16 or any(value is not None and (not isinstance(value, int) or not 0 <= value < 16) for value in frame_map):
        parser.error("--frame-map must be a 16-item JSON array of null or source cell indexes 0..15")

    args.layers_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = args.layers_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    args.review_dir.mkdir(parents=True, exist_ok=True)

    source_cells: list[Image.Image] = []
    source_cell_boxes: list[list[int]] = []
    for source_index in range(16):
        col, row = source_index % 4, source_index // 4
        x0, x1 = round(col * width / 4), round((col + 1) * width / 4)
        y0, y1 = round(row * height / 4), round((row + 1) * height / 4)
        trail = atlas.crop((x0, y0, x1, y1)).resize((160, 160), Image.Resampling.LANCZOS)
        gray = trail.convert("RGB").convert("L")
        color_channels = colorize_luminance(gray)
        alpha = trail.getchannel("A").point(lambda value: 0 if value < 8 else round(value * args.opacity))
        normalized = Image.merge("RGBA", (*color_channels, alpha))
        source_cells.append(normalized)
        source_cell_boxes.append([x0, y0, x1, y1])

    trails: list[Image.Image] = []
    frame_records: list[dict[str, object]] = []
    for index, source_index in enumerate(frame_map):
        normalized = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        if source_index is not None:
            normalized.alpha_composite(source_cells[source_index], (args.offset_x, args.offset_y))
        normalized.save(frames_dir / f"weaponlight_se_{index:02}.png")
        trails.append(normalized)

        visible_alpha = normalized.getchannel("A").point(lambda value: 255 if value >= 8 else 0)
        bbox = visible_alpha.getbbox()
        frame_records.append({
            "frame_index": index,
            "phase": timeline_frames[index]["phase"],
            "duration_ms": durations[index],
            "active": bbox is not None,
            "source_atlas_cell_index": source_index,
            "alpha_bbox_xyxy": list(bbox) if bbox else [],
            "source_cell_xyxy": source_cell_boxes[source_index] if source_index is not None else [],
        })

    write_strip(trails, args.layers_dir / "weaponlight-se-16.png")
    write_transparent_contact_sheet(trails, args.layers_dir / "weaponlight-se-4x4.png")

    poses: list[Image.Image] = []
    for index in range(16):
        pose_path = args.frames_dir / f"se_{index:02}.png"
        if not pose_path.exists():
            parser.error(f"missing character frame: {pose_path}")
        pose = Image.open(pose_path).convert("RGBA")
        if pose.size != (160, 160):
            parser.error(f"character frames must be 160x160; {pose_path} is {pose.size}")
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

    background = (235, 235, 235, 255)
    write_contact_sheet(behind, args.review_dir / "weaponlight-behind-contact-4x4.png", background)
    write_contact_sheet(over, args.review_dir / "weaponlight-over-contact-4x4.png", background)
    write_gif(behind, durations, args.review_dir / "basicattack-se-weaponlight-behind-one-shot.gif", args.scale)
    encoded_duration = write_gif(over, durations, args.review_dir / "basicattack-se-weaponlight-one-shot.gif", args.scale)

    provenance = {
        "status": "REVIEW_ONLY_SE_WEAPONLIGHT_NOT_RUNTIME_APPROVED",
        "source_atlas": str(args.atlas.resolve()),
        "source_atlas_sha256": sha256(args.atlas),
        "character_frames_dir": str(args.frames_dir.resolve()),
        "timeline": str(args.timeline.resolve()),
        "timeline_sha256": sha256(args.timeline),
        "normalization": {
            "source_grid": [4, 4],
            "source_size_px": [width, height],
            "output_cell_px": [160, 160],
            "color": "original plum-shadow to lavender-silver to warm-ivory gradient; source alpha preserved",
            "color_ramp_luminance_stops": COLOR_RAMP,
            "opacity_multiplier": args.opacity,
            "alpha_below_8_removed": True,
            "output_frame_to_source_cell_map": frame_map,
            "global_offset_px": [args.offset_x, args.offset_y],
            "registration": "shared fixed transform for all frames; no per-frame recentering or warp",
        },
        "playback": {
            "frame_count": 16,
            "duration_source_ms": sum(durations),
            "gif_duration_ms_with_recovery_hold": encoded_duration,
            "gif_loops": False,
            "final_recovery_hold_ms": max(600, durations[-1]),
            "gif_timing_quantization_ms": 10,
            "production_action_loop": False,
            "contact_phase": timeline.get("semantic_phases", {}).get("contact"),
        },
        "frames": frame_records,
        "outputs": {
            "layer_vertical_strip": str((args.layers_dir / "weaponlight-se-16.png").resolve()),
            "layer_contact_sheet": str((args.layers_dir / "weaponlight-se-4x4.png").resolve()),
            "behind_contact_sheet": str((args.review_dir / "weaponlight-behind-contact-4x4.png").resolve()),
            "over_contact_sheet": str((args.review_dir / "weaponlight-over-contact-4x4.png").resolve()),
            "behind_one_shot_gif": str((args.review_dir / "basicattack-se-weaponlight-behind-one-shot.gif").resolve()),
            "over_one_shot_gif": str((args.review_dir / "basicattack-se-weaponlight-one-shot.gif").resolve()),
        },
        "limitations": [
            "Single SE direction only.",
            "Existing character master still contains red fringe and clipped blade pixels in the strike segment.",
            "Image-generated effect has not been owner-approved and is not imported to runtime.",
            "This pass changes semantic contact timing only; source motion curves and sampled poses are unchanged.",
        ],
    }
    provenance_path = args.review_dir / "weaponlight-atlas-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "frame_count": len(trails),
        "source_cell_map": frame_map,
        "active_frames_1_based": [record["frame_index"] + 1 for record in frame_records if record["active"]],
        "source_duration_ms": sum(durations),
        "gif_duration_ms_with_hold": encoded_duration,
        "layers_dir": str(args.layers_dir),
        "review_dir": str(args.review_dir),
        "provenance_sha256": sha256(provenance_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
