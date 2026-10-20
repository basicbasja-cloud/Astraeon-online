#!/usr/bin/env python3
"""Build source-aligned Rokoko vs layered-paint GIF and contact reviews."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.character_factory_v3.paint_rokoko_trail_from_blade_path import (  # noqa: E402
    CELL,
    keep_trail_behind_head,
)


BACKGROUND = (242, 240, 238)
GUIDE_DIR = Path("source/rokoko-blender-guide")
LAYERS = ("BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "Headgear")


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def source_label(source_frame: float) -> str:
    value = f"{source_frame:g}"
    return value


def save_one_shot_gif(frames: list[Image.Image], durations: list[int], path: Path,
                      recovery_hold_ms: int) -> int:
    held = list(durations)
    held[-1] = max(held[-1], recovery_hold_ms)
    total_units = round(sum(held) / 10)
    units = [duration // 10 for duration in held]
    rest = total_units - sum(units)
    order = sorted(range(len(held)), key=lambda i: (-(held[i] % 10), i))
    for index in order[:rest]:
        units[index] += 1
    delays = [unit * 10 for unit in units]

    # Sample every frame at thumbnail size to build one shared GIF palette while
    # keeping the 1920x1024 review sequence practical to encode in memory.
    palette_source = Image.new("RGB", (480, 256 * len(frames)), BACKGROUND)
    for index, frame in enumerate(frames):
        palette_source.paste(frame.resize((480, 256), Image.Resampling.LANCZOS),
                             (0, index * 256))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=delays,
                    disposal=2, optimize=False)
    return sum(delays)


def compose_frame(iteration: Path, index: int, audit_frame: dict) -> Image.Image:
    result = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    for name in LAYERS[:3]:
        path = iteration / "layers" / name / "frames" / f"se_{index:02d}.png"
        result.alpha_composite(Image.open(path).convert("RGBA"))

    effect_path = iteration / "layers/WeaponLight/frames" / f"weaponlight_se_{index:02d}.png"
    effect = Image.open(effect_path).convert("RGBA")
    correction = int(audit_frame.get("pixel_root_correction_y", 0))
    head = audit_frame["landmarks_xy"]["head"]
    effect = keep_trail_behind_head(effect, [float(head[0]), float(head[1]) + correction])
    result.alpha_composite(effect)

    for name in LAYERS[3:]:
        path = iteration / "layers" / name / "frames" / f"se_{index:02d}.png"
        result.alpha_composite(Image.open(path).convert("RGBA"))
    return result


def comparison_frame(guide: Image.Image, painted: Image.Image,
                     index: int, source: float, total: int) -> Image.Image:
    canvas = Image.new("RGB", (1920, 1024), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    label_font = font(28)
    draw.text((24, 16), f"Rokoko guide | source {source_label(source)} | {index + 1}/{total}",
              fill=(25, 25, 29), font=label_font)
    draw.text((984, 16), f"Painted layers + WeaponLight | source {source_label(source)}",
              fill=(25, 25, 29), font=label_font)
    left = guide.convert("RGBA").resize((960, 960), Image.Resampling.LANCZOS)
    right = painted.convert("RGBA").resize((960, 960), Image.Resampling.LANCZOS)
    canvas.paste(left.convert("RGB"), (0, 64))
    canvas.paste(right.convert("RGB"), (960, 64))
    return canvas


def save_contact(guides: list[Image.Image], painted: list[Image.Image],
                 sources: list[float], path: Path) -> None:
    columns, rows = 4, math.ceil(len(guides) / 4)
    cell_width, cell_height = 640, 344
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    label_font = font(18)
    for index, (guide, art, source) in enumerate(zip(guides, painted, sources)):
        x, y = (index % columns) * cell_width, (index // columns) * cell_height
        draw.text((x + 5, y + 2), f"{index:02d} | source {source_label(source)}",
                  fill=(25, 25, 29), font=label_font)
        guide_cell = guide.convert("RGBA").resize((320, 320), Image.Resampling.LANCZOS)
        art_cell = art.convert("RGBA").resize((320, 320), Image.Resampling.LANCZOS)
        sheet.paste(guide_cell.convert("RGB"), (x, y + 24))
        sheet.paste(art_cell.convert("RGB"), (x + 320, y + 24))
    sheet.save(path)


def save_keyframe_review(guides: list[Image.Image], painted: list[Image.Image],
                         sources: list[float], wanted_sources: list[float], path: Path) -> None:
    indices = [min(range(len(sources)), key=lambda i: abs(sources[i] - wanted))
               for wanted in wanted_sources]
    tile = 512
    label_band = 48
    canvas = Image.new("RGB", (len(indices) * tile, 2 * tile + label_band), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    label_font = font(20)
    draw.text((8, 12), "Rokoko guide", fill=(25, 25, 29), font=label_font)
    draw.text((8, tile + label_band + 12), "Painted layered candidate",
              fill=(25, 25, 29), font=label_font)
    for column, index in enumerate(indices):
        x = column * tile
        draw.text((x + 8, tile + 12), f"source {source_label(sources[index])}",
                  fill=(25, 25, 29), font=label_font)
        guide = guides[index].convert("RGBA").resize((tile, tile), Image.Resampling.LANCZOS)
        art = painted[index].convert("RGBA").resize((tile, tile), Image.Resampling.LANCZOS)
        canvas.paste(guide.convert("RGB"), (x, label_band))
        canvas.paste(art.convert("RGB"), (x, tile + label_band))
    canvas.save(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration-root", type=Path, required=True)
    args = parser.parse_args()
    iteration = args.iteration_root.resolve()
    guide_root = iteration / GUIDE_DIR
    timeline = json.loads((guide_root / "motion-timeline.json").read_text())
    manifest = json.loads((guide_root / "motion-guide-manifest.json").read_text())
    provenance_path = iteration / "review/basicattack-se-rokoko-research-surface-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    trail_path = iteration / "review/weaponlight-path-provenance.json"
    trail = json.loads(trail_path.read_text())
    timeline_frames = timeline["frames"]
    pose_frames = provenance["frames"]
    trail_frames = trail["frames"]
    count = len(timeline_frames)
    if not (count == len(pose_frames) == len(trail_frames) == len(manifest["frames"])):
        parser.error("guide, painted pose, and WeaponLight frame counts must match exactly")

    sources = [float(frame["source_frame"]) for frame in timeline_frames]
    for index in range(count):
        for name, record in (("pose", pose_frames[index]), ("trail", trail_frames[index]),
                             ("manifest", manifest["frames"][index])):
            if not math.isclose(sources[index], float(record["source_frame"]), abs_tol=1e-5):
                parser.error(f"{name} frame {index} is not aligned to source frame {sources[index]}")

    guides: list[Image.Image] = []
    painted: list[Image.Image] = []
    comparison: list[Image.Image] = []
    for index, source in enumerate(sources):
        guide_path = guide_root / manifest["frames"][index]["guide_png"]
        guide = Image.open(guide_path).convert("RGBA")
        art = compose_frame(iteration, index, pose_frames[index])
        guides.append(guide)
        painted.append(art)
        comparison.append(comparison_frame(guide, art, index, source, count))

    review = iteration / "review"
    review.mkdir(parents=True, exist_ok=True)
    duration_values = [int(frame["duration_ms"]) for frame in timeline_frames]
    gif_path = review / "rokoko-vs-swordsman-one-shot.gif"
    duration = save_one_shot_gif(comparison, duration_values, gif_path,
                                 int(timeline.get("recovery_hold_ms", 300)))
    contact_path = review / f"rokoko-vs-swordsman-contact-4x{math.ceil(count / 4)}.png"
    save_contact(guides, painted, sources, contact_path)
    strike_path = review / "rokoko-vs-swordsman-strike-detail.png"
    save_keyframe_review(guides, painted, sources,
                         [498.0, 498.5, 499.0, 499.5, 500.0, 501.0], strike_path)
    elbow_path = review / "elbow-transition-497-to-497p5.png"
    save_keyframe_review(guides, painted, sources,
                         [497.0, 497.25, 497.375, 497.5], elbow_path)
    provenance["playback"]["comparison_gif_frame_count"] = count
    provenance["playback"]["comparison_gif_duration_ms"] = duration
    provenance["playback"]["comparison_contact_sheet"] = contact_path.name
    provenance["playback"]["gif_loop_extension"] = False
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    trail["playback"]["frame_count"] = count
    trail["playback"]["gif_duration_ms_with_recovery_hold"] = duration
    trail_path.write_text(json.dumps(trail, indent=2) + "\n")
    print(json.dumps({
        "frame_count": count,
        "duration_ms": duration,
        "comparison_gif": str(gif_path),
        "contact": str(contact_path),
        "strike_detail": str(strike_path),
        "elbow_transition": str(elbow_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
