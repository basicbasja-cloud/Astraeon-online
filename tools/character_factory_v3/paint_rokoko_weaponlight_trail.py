#!/usr/bin/env python3
"""Draw a thick, source-timed SE WeaponLight ribbon for the Rokoko sword strike.

The ribbon is an original 2D effect layer. Its onset and sweep direction follow
the sampled Rokoko RightHand sword proxy; its curve is registered against the
painted SE blade poses to account for the intentionally longer fantasy sword.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


CELL = 320
SUPERSAMPLE = 4
GRID = 4

# Frame-fitted cubic trails in 320-cell pixels (top-left origin). Sample 6 is
# the small onset at the overhead blade; sample 7 begins the sweep, and sample
# 8 starts the broad downward stroke. The later curves follow the lower,
# rightward follow-through shown by the Rokoko guide. These are original curves,
# not copied RO sprites.
FRAME_CURVES: dict[int, tuple[tuple[float, float], ...]] = {
    6: ((150, 48), (154, 44), (160, 43), (166, 45)),
    7: ((151, 49), (174, 41), (197, 43), (211, 55)),
    8: ((211, 54), (224, 88), (180, 143), (143, 192)),
    9: ((208, 63), (226, 108), (190, 158), (162, 204)),
    10: ((199, 77), (212, 124), (184, 174), (174, 210)),
    11: ((188, 95), (202, 136), (170, 184), (156, 210)),
    12: ((176, 111), (190, 144), (166, 174), (159, 199)),
    13: ((165, 126), (178, 148), (161, 175), (156, 190)),
}

# Per-frame opacity and maximum width in the 320px authoring cell.
FRAME_PROFILE: dict[int, tuple[float, float]] = {
    6: (0.16, 8.0),   # faint trail onset while the blade starts moving
    7: (0.34, 17.0),
    8: (0.76, 45.0),
    9: (0.87, 48.0),  # broadest contact/follow-through beat
    10: (0.72, 42.0),
    11: (0.50, 34.0),
    12: (0.30, 25.0),
    13: (0.14, 16.0),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cubic(span: tuple[tuple[float, float], ...], t: float) -> tuple[float, float]:
    p0, p1, p2, p3 = (np.asarray(point, dtype=np.float64) for point in span)
    u = 1.0 - t
    point = u**3 * p0 + 3 * u**2 * t * p1 + 3 * u * t**2 * p2 + t**3 * p3
    return float(point[0]), float(point[1])


def ribbon_mask(curve: tuple[tuple[float, float], ...], maximum_width: float,
                band_scale: float = 1.0) -> Image.Image:
    """Rasterize one continuous, tapered ribbon silhouette at 4x resolution."""
    scale = SUPERSAMPLE
    mask = Image.new("L", (CELL * scale, CELL * scale), 0)
    draw = ImageDraw.Draw(mask)
    steps = 160
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        x, y = cubic(curve, t)
        before = cubic(curve, max(0.0, t - 0.002))
        after = cubic(curve, min(1.0, t + 0.002))
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = max(math.hypot(dx, dy), 1e-6)
        nx, ny = -dy / length, dx / length
        # Taper to a true point at both ends; the middle remains broad like the
        # owner's RO reference, but has no bulb-shaped caps or scanline seams.
        envelope = max(0.0, math.sin(math.pi * t)) ** 0.78
        half = maximum_width * band_scale * envelope / 2
        left.append(((x + nx * half) * scale, (y + ny * half) * scale))
        right.append(((x - nx * half) * scale, (y - ny * half) * scale))
    draw.polygon(left + list(reversed(right)), fill=255)
    return mask


def fill_mask(color: tuple[int, int, int], alpha: float, mask: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", mask.size, (*color, 0))
    layer.putalpha(mask.point(lambda value: round(value * alpha)))
    return layer.resize((CELL, CELL), Image.Resampling.LANCZOS)


def make_trail(index: int) -> Image.Image:
    frame = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if index not in FRAME_PROFILE:
        return frame
    opacity, max_width = FRAME_PROFILE[index]
    curve = FRAME_CURVES[index]

    # Three clean, aligned masks give the plume an original RO-like lavender
    # gradient: plum-gray edge, silver-lavender body, and a narrow warm core.
    outer = ribbon_mask(curve, max_width + 8, 1.0)
    body = ribbon_mask(curve, max_width * 0.82, 1.0)
    core = ribbon_mask(curve, max(2.4, max_width * 0.23), 1.0)
    frame.alpha_composite(fill_mask((105, 96, 127), opacity * 0.66, outer))
    frame.alpha_composite(fill_mask((178, 174, 210), opacity * 0.82, body))
    frame.alpha_composite(fill_mask((255, 244, 222), opacity * 0.88, core))
    return frame


def contact_sheet(frames: list[Image.Image], background: tuple[int, int, int]) -> Image.Image:
    result = Image.new("RGBA", (CELL * GRID, CELL * GRID), (*background, 255))
    for index, frame in enumerate(frames):
        result.alpha_composite(frame, ((index % GRID) * CELL, (index // GRID) * CELL))
    return result


def make_gif(frames: list[Image.Image], durations: list[int], path: Path,
             scale: int, final_hold_ms: int) -> int:
    held = list(durations)
    held[-1] = max(held[-1], final_hold_ms)
    # GIF stores duration in 10ms units. Preserve cumulative source timing.
    total_units = round(sum(held) / 10)
    units = [duration // 10 for duration in held]
    remaining = total_units - sum(units)
    order = sorted(range(len(held)), key=lambda i: (-(held[i] % 10), i))
    for index in order[:remaining]:
        units[index] += 1
    encoded_durations = [max(10, unit * 10) for unit in units]

    canvases = []
    for frame in frames:
        canvas = Image.new("RGBA", (CELL, CELL), (235, 235, 235, 255))
        canvas.alpha_composite(frame)
        if scale != 1:
            canvas = canvas.resize((CELL * scale, CELL * scale), Image.Resampling.LANCZOS)
        canvases.append(canvas.convert("RGB"))
    palette_source = Image.new("RGB", (canvases[0].width, canvases[0].height * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * canvas.height))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in canvases]
    # No loop extension: this is a genuine one-shot review playback.
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=encoded_durations,
                    disposal=2, optimize=False)
    return sum(encoded_durations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master-frames", required=True, type=Path)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--projected-path", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--scale", type=int, default=3)
    parser.add_argument("--final-hold-ms", type=int, default=600)
    args = parser.parse_args()
    if args.scale < 1 or args.final_hold_ms < 350:
        parser.error("scale must be positive and recovery hold must be at least 350ms")

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    projection = json.loads(args.projected_path.read_text(encoding="utf-8"))
    if len(timeline.get("frames", [])) != 16 or len(projection.get("records", [])) != 16:
        parser.error("timeline and projected sword path must each contain 16 samples")
    durations = [int(item["duration_ms"]) for item in timeline["frames"]]
    if any(projection["records"][i]["source_frame"] != timeline["frames"][i]["source_frame"]
           for i in range(16)):
        parser.error("projected path source frame IDs do not match the sprite timeline")

    args.output_root.mkdir(parents=True, exist_ok=True)
    layer_root = args.output_root / "layers" / "WeaponLight"
    frame_root = layer_root / "frames"
    review_root = args.output_root / "review"
    frame_root.mkdir(parents=True, exist_ok=True)
    review_root.mkdir(parents=True, exist_ok=True)

    effects = [make_trail(index) for index in range(16)]
    masters = []
    for index in range(16):
        path = args.master_frames / f"se_{index:02d}.png"
        if not path.exists():
            parser.error(f"missing normalized character frame: {path}")
        image = Image.open(path).convert("RGBA")
        if image.size != (CELL, CELL):
            parser.error(f"character frame must be {CELL}x{CELL}: {path} ({image.size})")
        masters.append(image)
        effects[index].save(frame_root / f"weaponlight_se_{index:02d}.png")

    layer_sheet = Image.new("RGBA", (CELL * GRID, CELL * GRID), (0, 0, 0, 0))
    vertical = Image.new("RGBA", (CELL, CELL * 16), (0, 0, 0, 0))
    behind: list[Image.Image] = []
    over: list[Image.Image] = []
    for index, (effect, master) in enumerate(zip(effects, masters)):
        xy = ((index % GRID) * CELL, (index // GRID) * CELL)
        layer_sheet.alpha_composite(effect, xy)
        vertical.alpha_composite(effect, (0, index * CELL))
        behind_frame = effect.copy()
        behind_frame.alpha_composite(master)
        behind.append(behind_frame)
        over_frame = master.copy()
        over_frame.alpha_composite(effect)
        over.append(over_frame)

    layer_sheet.save(layer_root / "weaponlight-se-4x4.png")
    vertical.save(layer_root / "weaponlight-se-16-strip.png")
    layer_sheet.convert("RGB").save(review_root / "weaponlight-layer-contact-4x4.jpg", quality=96)
    contact_sheet(behind, (235, 235, 235)).convert("RGB").save(review_root / "rokoko-basicattack-se-behind-contact-4x4.jpg", quality=96)
    contact_sheet(over, (235, 235, 235)).convert("RGB").save(review_root / "rokoko-basicattack-se-over-contact-4x4.jpg", quality=96)

    one_shot = review_root / "rokoko-basicattack-se-final-one-shot.gif"
    slow_motion = review_root / "rokoko-basicattack-se-final-slow-motion-one-shot.gif"
    normal_total = make_gif(behind, durations, one_shot, args.scale, args.final_hold_ms)
    slow_total = make_gif(behind, [duration * 2 for duration in durations], slow_motion,
                          args.scale, args.final_hold_ms * 2)

    frames_report: list[dict[str, Any]] = []
    for index, effect in enumerate(effects):
        profile = FRAME_PROFILE.get(index)
        frames_report.append({
            "sprite_frame": index,
            "source_frame": timeline["frames"][index]["source_frame"],
            "source_proxy_hand_xy_px": projection["records"][index]["hand_xy_px"],
            "source_proxy_tip_xy_px": projection["records"][index]["proxy_tip_xy_px"],
            "source_proxy_blade_delta_xy_px": projection["records"][index]["proxy_blade_delta_xy_px"],
            "trail_active": profile is not None,
            "curve_points_cell_px": [list(point) for point in FRAME_CURVES[index]] if profile else [],
            "opacity": profile[0] if profile else 0,
            "maximum_width_cell_px": profile[1] if profile else 0,
            "alpha_bounds_xyxy": list(effect.getchannel("A").getbbox() or []),
        })

    provenance = {
        "status": "INTERNAL_VISUAL_CANDIDATE_OWNER_REVIEW_PENDING",
        "action": "BasicAttack",
        "direction": "SE",
        "frame_count": 16,
        "master_frame_dir": str(args.master_frames.resolve()),
        "master_frame_sha256": [sha256(args.master_frames / f"se_{i:02d}.png") for i in range(16)],
        "timeline": str(args.timeline.resolve()),
        "timeline_sha256": sha256(args.timeline),
        "projected_rokoko_path": str(args.projected_path.resolve()),
        "projected_rokoko_path_sha256": sha256(args.projected_path),
        "art_direction": "Original thick diagonal hook ribbon, timed to Rokoko's raised-sword/downward strike; plum-gray rim, lavender-silver body and warm-ivory inner light.",
        "frame_curves_cell_px": {str(index): [list(point) for point in curve]
                                  for index, curve in FRAME_CURVES.items()},
        "width_profile": "smooth sine taper with a sharp point at both ends; max width varies by strike phase",
        "registration_method": "Rokoko projected RightHand axis determines strike direction and phase; 2D curve is fitted to painted sword tip positions because the fantasy sword is longer than the review proxy.",
        "composition": "WeaponLight remains an independent transparent layer. Main preview composites the effect behind the full painted character, preserving sword and glove readability.",
        "playback": {"normal_gif_duration_ms": normal_total, "slow_gif_duration_ms": slow_total,
                     "final_recovery_hold_ms": args.final_hold_ms, "gif_loop_extension": False,
                     "gif_review_scale": args.scale, "gif_palette_colors": 255},
        "frames": frames_report,
        "limitations": [
            "SE BasicAttack only; other directions and actions are not included.",
            "The 16 painted full-character frames remain a review master; semantic cutout layers, canonical V3 retarget, and game runtime integration are not completed.",
            "Frame artwork is an image-generation paintover and is not yet owner-approved.",
        ],
        "outputs": {
            "layer_contact": str((review_root / "weaponlight-layer-contact-4x4.jpg").resolve()),
            "behind_contact": str((review_root / "rokoko-basicattack-se-behind-contact-4x4.jpg").resolve()),
            "over_contact": str((review_root / "rokoko-basicattack-se-over-contact-4x4.jpg").resolve()),
            "normal_one_shot": str(one_shot.resolve()),
            "slow_motion_one_shot": str(slow_motion.resolve()),
            "transparent_layer_sheet": str((layer_root / "weaponlight-se-4x4.png").resolve()),
            "transparent_vertical_strip": str((layer_root / "weaponlight-se-16-strip.png").resolve()),
        },
    }
    provenance_path = review_root / "weaponlight-trail-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": provenance["status"],
        "active_frames_1_based": [i + 1 for i in FRAME_PROFILE],
        "normal_one_shot_duration_ms": normal_total,
        "slow_one_shot_duration_ms": slow_total,
        "normal_one_shot": str(one_shot),
        "behind_contact": str(review_root / "rokoko-basicattack-se-behind-contact-4x4.jpg"),
        "weaponlight_layer": str(layer_root / "weaponlight-se-4x4.png"),
        "provenance_sha256": sha256(provenance_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
