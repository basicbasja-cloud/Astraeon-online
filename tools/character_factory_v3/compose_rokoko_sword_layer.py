#!/usr/bin/env python3
"""Compose a reusable painted sword layer onto normalized Rokoko pose art.

The Blender guide contains hand landmarks and a wrist-axis proxy, not an authored
sword mesh. This tool uses the proxy only for its projected angle, extends the
painted blade to a controlled art length, and keeps the prop editable as its own
transparent layer. The character body remains an independent layer.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


def label_frame(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def transformed_point(point: tuple[float, float], size: tuple[int, int],
                      rotated_size: tuple[int, int], degrees_ccw: float,
                      scale: float) -> tuple[float, float]:
    width, height = size
    out_width, out_height = rotated_size
    cx, cy = width / 2, height / 2
    dx = (point[0] - cx) * scale
    dy = (point[1] - cy) * scale
    angle = math.radians(degrees_ccw)
    cosine, sine = math.cos(angle), math.sin(angle)
    # Pillow's positive rotate angle is visually counter-clockwise.
    return (
        out_width / 2 + cosine * dx + sine * dy,
        out_height / 2 - sine * dx + cosine * dy,
    )


def paste_clipped(destination: Image.Image, source: Image.Image,
                  xy: tuple[int, int]) -> None:
    x, y = xy
    left, top = max(0, x), max(0, y)
    right, bottom = min(destination.width, x + source.width), min(destination.height, y + source.height)
    if right <= left or bottom <= top:
        return
    crop = source.crop((left - x, top - y, right - x, bottom - y))
    destination.alpha_composite(crop, (left, top))


def prepare_sword(path: Path, tip: tuple[float, float], grip: tuple[float, float]) -> tuple[Image.Image, tuple[float, float], tuple[float, float]]:
    sword = Image.open(path).convert("RGBA")
    pixels = sword.load()
    removed = 0
    for y in range(sword.height):
        for x in range(sword.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha <= 5 or (alpha > 0 and red > 150 and green < 75 and blue < 95 and red > green * 1.8):
                if alpha > 0:
                    removed += 1
                    pixels[x, y] = (0, 0, 0, 0)
    bbox = sword.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError(f"sword source has no visible pixels after edge cleanup: {path}")
    cropped = sword.crop(bbox)
    return cropped, (tip[0] - bbox[0], tip[1] - bbox[1]), (grip[0] - bbox[0], grip[1] - bbox[1])


def render_weapon(sword: Image.Image, tip: tuple[float, float], grip: tuple[float, float],
                  destination_pivot: tuple[float, float], target_angle: float,
                  target_length: float, canvas_size: int) -> tuple[Image.Image, dict[str, object]]:
    source_length = math.dist(tip, grip)
    if source_length <= 1:
        raise ValueError("sword tip and grip must define a nonzero blade axis")
    scale = target_length / source_length
    resized_size = (max(1, round(sword.width * scale)), max(1, round(sword.height * scale)))
    resized = sword.resize(resized_size, Image.Resampling.LANCZOS)
    scaled_tip = (tip[0] * resized_size[0] / sword.width,
                  tip[1] * resized_size[1] / sword.height)
    scaled_grip = (grip[0] * resized_size[0] / sword.width,
                   grip[1] * resized_size[1] / sword.height)

    # A vertical source sword points up (screen angle -90 degrees). Rotate it
    # to the target hand-axis angle; the guide's proxy length is intentionally
    # ignored because it foreshortens dramatically when pointed toward camera.
    rotate_ccw = -(target_angle + 90.0)
    rotated = resized.rotate(rotate_ccw, resample=Image.Resampling.BICUBIC, expand=True)
    rotated_tip = transformed_point(scaled_tip, resized.size, rotated.size, rotate_ccw, 1.0)
    rotated_grip = transformed_point(scaled_grip, resized.size, rotated.size, rotate_ccw, 1.0)
    dx, dy = destination_pivot[0] - rotated_grip[0], destination_pivot[1] - rotated_grip[1]
    placed_tip = (rotated_tip[0] + dx, rotated_tip[1] + dy)
    actual_angle = math.degrees(math.atan2(placed_tip[1] - destination_pivot[1],
                                           placed_tip[0] - destination_pivot[0]))

    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    paste_clipped(layer, rotated, (round(dx), round(dy)))
    return layer, {
        "target_angle_degrees_screen": round(target_angle, 3),
        "rendered_angle_degrees_screen": round(actual_angle, 3),
        "target_blade_length_px": round(target_length, 3),
        "sword_source_to_output_scale": round(scale, 6),
        "grip_xy_output_px": [round(destination_pivot[0], 3), round(destination_pivot[1], 3)],
        "tip_xy_output_px": [round(placed_tip[0], 3), round(placed_tip[1], 3)],
    }


def hand_occlusion(body: Image.Image, weapon_and_body: Image.Image,
                   pivot: tuple[float, float], width: float, height: float) -> None:
    mask = Image.new("L", body.size, 0)
    draw = ImageDraw.Draw(mask)
    cx, cy = pivot
    draw.ellipse((cx - width / 2, cy - height / 2,
                  cx + width / 2, cy + height / 2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.4))
    body_alpha = ImageChops.multiply(body.getchannel("A"), mask)
    patch = body.copy()
    patch.putalpha(body_alpha)
    weapon_and_body.alpha_composite(patch)


def make_contact(rows: list[tuple[str, Image.Image]], path: Path,
                 cell_size: int = 480, columns: int = 3) -> None:
    row_height = cell_size + 28
    sheet = Image.new("RGB", (cell_size * columns, row_height * math.ceil(len(rows) / columns)), (238, 237, 235))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (label, frame) in enumerate(rows):
        preview = frame.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
        x, y = (index % columns) * cell_size, (index // columns) * row_height
        sheet.paste(preview, (x, y), preview)
        draw.text((x + 6, y + cell_size + 6), label, fill=(25, 25, 25), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body-root", type=Path, required=True,
                        help="normalized character frames, each containing the fist and no sword")
    parser.add_argument("--timeline", type=Path, required=True,
                        help="motion-timeline.json from normalize_rokoko_keyframes.py")
    parser.add_argument("--normalization-audit", type=Path, required=True)
    parser.add_argument("--guide-manifest", type=Path, required=True)
    parser.add_argument("--painted-grips", type=Path,
                        help=("optional JSON object mapping source-frame strings to painted fist coordinates "
                              "in normalized output pixels, e.g. {'498.5': {'x': 414, 'y': 590}}"))
    parser.add_argument("--sword", type=Path, required=True,
                        help="single high-quality upright transparent sword master image")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--tip", default="626,40", help="sword-master blade-tip pixel x,y")
    parser.add_argument("--grip", default="626,1080", help="sword-master hand-grip pixel x,y")
    parser.add_argument("--blade-height-ratio", type=float, default=0.36,
                        help="visible sword length divided by guide head-to-floor height")
    parser.add_argument("--hand-mask-width", type=float, default=58)
    parser.add_argument("--hand-mask-height", type=float, default=52)
    args = parser.parse_args()
    if not (0.1 <= args.blade_height_ratio <= 0.8):
        parser.error("--blade-height-ratio must be between 0.1 and 0.8")

    try:
        tip = tuple(map(float, args.tip.split(",")))
        grip = tuple(map(float, args.grip.split(",")))
    except ValueError:
        parser.error("--tip and --grip must be x,y pairs")
    if len(tip) != 2 or len(grip) != 2:
        parser.error("--tip and --grip must be x,y pairs")

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    normalization = json.loads(args.normalization_audit.read_text(encoding="utf-8"))
    guide = json.loads(args.guide_manifest.read_text(encoding="utf-8"))
    painted_grips = (json.loads(args.painted_grips.read_text(encoding="utf-8"))
                     if args.painted_grips else {})
    normalized_frames = timeline["frames"]
    audit_by_source = {float(item["source_frame"]): item for item in normalization["frames"]}
    guide_by_source = {float(item["source_frame"]): item for item in guide["frames"]}
    if painted_grips and not isinstance(painted_grips, dict):
        parser.error("--painted-grips must contain a JSON object keyed by source-frame number")
    if painted_grips:
        required_grips = {str(float(record["source_frame"])) for record in normalized_frames}
        missing_grips = sorted(required_grips - set(painted_grips))
        if missing_grips:
            parser.error(f"--painted-grips is missing source frames: {', '.join(missing_grips)}")
    sword, cropped_tip, cropped_grip = prepare_sword(args.sword, tip, grip)
    canvas_value = normalization["canvas_size_px"]
    canvas_size = int(canvas_value[0] if isinstance(canvas_value, list) else canvas_value)
    root_x, root_y = map(float, normalization["root_xy_px"])
    output = args.output_root
    character_dir = output / "layers" / "Character" / "frames"
    weapon_dir = output / "layers" / "Weapon" / "frames"
    composite_dir = output / "composite" / "frames"
    for directory in (character_dir, weapon_dir, composite_dir):
        directory.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    character_contact: list[tuple[str, Image.Image]] = []
    weapon_contact: list[tuple[str, Image.Image]] = []
    composite_contact: list[tuple[str, Image.Image]] = []
    gif_frames: list[Image.Image] = []
    gif_delays: list[int] = []
    for record in normalized_frames:
        source_frame = float(record["source_frame"])
        audit = audit_by_source[source_frame]
        guide_record = guide_by_source[source_frame]
        sprite_index = int(record["sprite_frame"])
        body_path = args.body_root / "frames" / f"basicattack_se_{sprite_index:02d}.png"
        if not body_path.is_file():
            body_path = args.body_root / f"basicattack_se_{sprite_index:02d}.png"
        if not body_path.is_file():
            raise FileNotFoundError(f"normalized body frame is missing: {body_path}")
        body = Image.open(body_path).convert("RGBA")
        if body.size != (canvas_size, canvas_size):
            raise ValueError(f"{body_path} must be {canvas_size}x{canvas_size}, got {body.size}")

        landmarks = guide_record["body_landmarks_xy_px"]
        support_foot_name = max(("foot_R", "foot_L"), key=lambda name: landmarks[name][0])
        support_x, support_y = map(float, landmarks[support_foot_name])
        ratio = (float(audit["scale"]) * float(audit["source_head_to_floor_px"])
                 / float(audit["guide_head_to_floor_px"]))
        hand_x, hand_y = map(float, guide_record["right_hand_palm_xy_px"])
        grip_override = painted_grips.get(str(source_frame))
        if grip_override is not None:
            pivot = (float(grip_override["x"]), float(grip_override["y"]))
            pivot_source = "painted_fist_annotation"
        else:
            pivot = (root_x + (hand_x - support_x) * ratio,
                     root_y + (hand_y - support_y) * ratio)
            pivot_source = "guide_palm_projected_from_support_foot"
        wrist_x, wrist_y = map(float, guide_record["right_hand_wrist_xy_px"])
        angle = math.degrees(math.atan2(hand_y - wrist_y, hand_x - wrist_x))
        target_length = float(audit["guide_head_to_floor_px"]) * ratio * args.blade_height_ratio
        weapon, weapon_audit = render_weapon(sword, cropped_tip, cropped_grip,
                                             pivot, angle, target_length, canvas_size)
        composite = body.copy()
        composite.alpha_composite(weapon)
        hand_occlusion(body, composite, pivot, args.hand_mask_width, args.hand_mask_height)

        label = f"{sprite_index:02d} / {source_frame:g}"
        character_out = character_dir / f"se_{sprite_index:02d}.png"
        weapon_out = weapon_dir / f"se_{sprite_index:02d}.png"
        composite_out = composite_dir / f"se_{sprite_index:02d}.png"
        body.save(character_out, optimize=True)
        weapon.save(weapon_out, optimize=True)
        composite.save(composite_out, optimize=True)
        character_contact.append((label, body))
        weapon_contact.append((label, weapon))
        composite_contact.append((label, composite))
        gif_frames.append(composite.resize((512, 512), Image.Resampling.LANCZOS))
        gif_delays.append(int(record["duration_ms_exact"]))
        records.append({
            "sprite_frame": sprite_index,
            "source_frame": source_frame,
            "guide_support_foot": support_foot_name,
            "guide_palm_xy_px": [round(hand_x, 3), round(hand_y, 3)],
            "output_pivot_xy_px": [round(pivot[0], 3), round(pivot[1], 3)],
            "pivot_source": pivot_source,
            "output_guide_scale": round(ratio, 6),
            **weapon_audit,
            "character_layer": str(character_out.relative_to(output)),
            "weapon_layer": str(weapon_out.relative_to(output)),
            "composite": str(composite_out.relative_to(output)),
        })

    review = output / "review"
    review.mkdir(parents=True, exist_ok=True)
    make_contact(character_contact, review / "character-layer-contact.png")
    make_contact(weapon_contact, review / "weapon-layer-contact.png")
    make_contact(composite_contact, review / "composite-contact.png")
    if gif_frames:
        gif_frames[0].save(review / "weapon-layer-one-shot.gif", save_all=True,
                           append_images=gif_frames[1:], duration=gif_delays,
                           disposal=2, optimize=False)
    (review / "weapon-layer-audit.json").write_text(json.dumps({
        "status": "LAYERED_REVIEW_ONLY",
        "weapon_method": "one painted sword master, transformed rigidly around the Rokoko hand pivot; the proxy's projected length is not used",
        "blade_height_ratio": args.blade_height_ratio,
        "source_sword": str(args.sword),
        "sword_master_tip_xy_px": list(tip),
        "sword_master_grip_xy_px": list(grip),
        "hand_occlusion_mask_px": [args.hand_mask_width, args.hand_mask_height],
        "painted_grip_annotations": painted_grips,
        "frames": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"frames": len(records), "output": str(output),
                      "review_gif": str(review / "weapon-layer-one-shot.gif"),
                      "audit": str(review / "weapon-layer-audit.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
