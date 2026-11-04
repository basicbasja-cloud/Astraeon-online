#!/usr/bin/env python3
"""Make enlarged, annotated hand-to-tip crops from Rokoko Blender guides.

The pink arrow is an authoring overlay for paintovers and image-generation
references. It is not part of the character or weapon artwork.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


def frame_label(value: float) -> str:
    text = f"{float(value):g}"
    return text.replace(".", "p")


def make_detail(guide: Image.Image, grip: list[float], tip: list[float],
                output_size: int) -> tuple[Image.Image, dict[str, object]]:
    width, height = guide.size
    distance = math.dist(grip, tip)
    crop_size = max(320, min(640, math.ceil(distance * 1.6 / 16) * 16))
    crop_size = min(crop_size, width, height)
    center_x = (float(grip[0]) + float(tip[0])) / 2
    center_y = (float(grip[1]) + float(tip[1])) / 2
    left = round(center_x - crop_size / 2)
    top = round(center_y - crop_size / 2)
    left = min(max(0, left), width - crop_size)
    top = min(max(0, top), height - crop_size)

    detail = guide.crop((left, top, left + crop_size, top + crop_size)).resize(
        (output_size, output_size), Image.Resampling.LANCZOS
    ).convert("RGBA")
    factor = output_size / crop_size
    start = ((float(grip[0]) - left) * factor, (float(grip[1]) - top) * factor)
    end = ((float(tip[0]) - left) * factor, (float(tip[1]) - top) * factor)
    draw = ImageDraw.Draw(detail)
    for line_width, color in [(17, (15, 15, 20, 255)), (9, (255, 42, 112, 255))]:
        draw.line([start, end], fill=color, width=line_width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    for offset in (2.55, -2.55):
        point = (end[0] + 34 * math.cos(angle + offset),
                 end[1] + 34 * math.sin(angle + offset))
        draw.line([end, point], fill=(15, 15, 20, 255), width=17)
        draw.line([end, point], fill=(255, 42, 112, 255), width=9)
    for point, color in [(start, (255, 237, 72, 255)), (end, (255, 255, 255, 255))]:
        radius = 13
        draw.ellipse((point[0] - radius, point[1] - radius,
                      point[0] + radius, point[1] + radius),
                     fill=color, outline=(15, 15, 20, 255), width=5)
    return detail, {
        "crop_xywh": [left, top, crop_size, crop_size],
        "grip_xy_guide": list(map(float, grip)),
        "tip_xy_guide": list(map(float, tip)),
        "axis_degrees_screen": round(math.degrees(math.atan2(
            float(tip[1]) - float(grip[1]), float(tip[0]) - float(grip[0])
        )), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide-root", type=Path, required=True)
    parser.add_argument("--guide-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--size", type=int, default=768)
    args = parser.parse_args()
    if args.size < 256:
        parser.error("--size must be at least 256 pixels")

    manifest = json.loads(args.guide_manifest.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for frame in manifest["frames"]:
        grip = frame.get("right_hand_palm_xy_px")
        tip = frame.get("proxy_tip_xy_px")
        if grip is None or tip is None:
            continue
        guide = Image.open(args.guide_root / frame["guide_png"]).convert("RGBA")
        detail, audit = make_detail(guide, grip, tip, args.size)
        filename = f"weapon-guide-{frame_label(frame['source_frame'])}.png"
        detail.save(args.output_dir / filename, optimize=True)
        records.append({
            "source_frame": frame["source_frame"],
            "guide_png": frame["guide_png"],
            "weapon_guide_detail_png": filename,
            "proxy_angle_degrees": frame.get("proxy_angle_degrees"),
            **audit,
        })
    audit_path = args.output_dir / "weapon-guide-details-manifest.json"
    audit_path.write_text(json.dumps({
        "status": "REVIEW_GUIDES_ONLY",
        "annotation": "pink arrow marks the guide grip-to-tip axis; it is not artwork",
        "frames": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"frames": len(records), "output_dir": str(args.output_dir),
                      "manifest": str(audit_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
