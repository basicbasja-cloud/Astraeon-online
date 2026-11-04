#!/usr/bin/env python3
"""Warp the research SE cutouts to projected Rokoko joints for a review-only study.

This ports the fixed-source-triangulation method from research candidate-06.
It keeps the source master art and shared canvas intact, while replacing its
custom pose sequence with the sampled Rokoko body landmarks. Output is a visual
study and is not production approved.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import Delaunay

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.character_factory_v3.prepare_basicattack_sheet import find_foot_baseline  # noqa: E402


CELL = 320
LAYERS = ["BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "Headgear"]
BODY_POINTS = [
    "head", "neck", "waist",
    "shoulder_R", "elbow_R", "hand_R",
    "shoulder_L", "elbow_L", "hand_L",
    "hip_R", "knee_R", "foot_R",
    "hip_L", "knee_L", "foot_L",
]
BACKGROUND = (235, 235, 235)


def signed_area(points: np.ndarray) -> np.ndarray:
    a, b, c = points[:, 0], points[:, 1], points[:, 2]
    return ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1])
            - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])) / 2.0


def source_points(guide: dict[str, object]) -> tuple[list[str], np.ndarray]:
    names = ["corner_tl", "corner_tr", "corner_br", "corner_bl", *BODY_POINTS]
    points = [
        (0.0, 0.0), (CELL - 1.0, 0.0),
        (CELL - 1.0, CELL - 1.0), (0.0, CELL - 1.0),
    ]
    points.extend(tuple(map(float, guide[name])) for name in BODY_POINTS)
    head_x, head_y = map(float, guide["head"])
    for name, dx, dy in [
        ("head_tl", -30, -28), ("head_tr", 30, -28),
        ("head_bl", -30, 16), ("head_br", 30, 16),
    ]:
        names.append(name)
        points.append((head_x + dx, head_y + dy))
    return names, np.asarray(points, dtype=np.float64)


def target_points(frame: dict[str, object], image_size: int, guide: dict[str, object],
                  root_x: int, root_y: int) -> tuple[np.ndarray, dict[str, float]]:
    raw = frame.get("body_landmarks_xy_px")
    if not isinstance(raw, dict) or any(name not in raw for name in BODY_POINTS):
        raise ValueError(f"frame {frame.get('sprite_frame')} has incomplete body landmarks")
    factor = CELL / image_size
    points = {name: np.asarray(raw[name], dtype=np.float64) * factor for name in BODY_POINTS}

    # Keep the pelvis on the shared horizontal root and place the lower shoe
    # contact on one shared floor line. The projected body pose remains intact.
    dx = float(root_x) - float(points["waist"][0])
    support_y = max(float(points["foot_R"][1]), float(points["foot_L"][1]))
    dy = float(root_y) - support_y
    for point in points.values():
        point += (dx, dy)

    source_names, source = source_points(guide)
    target: list[tuple[float, float]] = [
        (0.0, 0.0), (CELL - 1.0, 0.0),
        (CELL - 1.0, CELL - 1.0), (0.0, CELL - 1.0),
    ]
    target.extend(tuple(points[name]) for name in BODY_POINTS)
    head_dx = points["head"][0] - float(guide["head"][0])
    head_dy = points["head"][1] - float(guide["head"][1])
    for _, dx_head, dy_head in [
        ("head_tl", -30, -28), ("head_tr", 30, -28),
        ("head_bl", -30, 16), ("head_br", 30, 16),
    ]:
        target.append((float(guide["head"][0]) + dx_head + head_dx,
                       float(guide["head"][1]) + dy_head + head_dy))
    target_array = np.asarray(target, dtype=np.float64)
    if len(source_names) != len(target_array):
        raise AssertionError("source and target control-point counts differ")
    return target_array, {"root_dx_px": dx, "floor_dy_px": dy}


def warp_rgba(image: Image.Image, source: np.ndarray, target: np.ndarray,
              triangles: np.ndarray) -> tuple[Image.Image, int]:
    """Apply the research fixed-topology forward warp in premultiplied RGBA."""
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float64) / 255.0
    src = rgba.copy()
    src[:, :, :3] *= src[:, :, 3:4]
    out = np.zeros_like(src)
    flipped = 0

    src_areas = signed_area(source[triangles])
    dst_areas = signed_area(target[triangles])
    flipped = int(np.count_nonzero(src_areas * dst_areas < -1e-4))
    height, width = rgba.shape[:2]
    for tri_index, indices in enumerate(triangles):
        original = source[indices]
        posed = target[indices]
        x0, y0 = np.maximum(0, np.floor(posed.min(axis=0))).astype(int)
        x1, y1 = np.minimum([width - 1, height - 1], np.ceil(posed.max(axis=0))).astype(int)
        if x1 < x0 or y1 < y0 or abs(dst_areas[tri_index]) < 1e-6:
            continue
        matrix = np.vstack((posed.T, np.ones(3)))
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        pixels = np.vstack((xx.ravel(), yy.ravel(), np.ones(xx.size)))
        barycentric = np.linalg.solve(matrix, pixels).T
        inside = np.all(barycentric >= -1e-7, axis=1)
        if not np.any(inside):
            continue
        coordinates = barycentric[inside] @ original
        colors = np.column_stack([
            ndimage.map_coordinates(
                src[:, :, channel], coordinates[:, ::-1].T,
                order=1, mode="constant", cval=0.0,
            )
            for channel in range(4)
        ])
        ix, iy = xx.ravel()[inside], yy.ravel()[inside]
        old = out[iy, ix]
        out[iy, ix] = colors + old * (1.0 - colors[:, 3:4])

    out[:, :, :3] = np.divide(
        out[:, :, :3], out[:, :, 3:4], out=np.zeros_like(out[:, :, :3]),
        where=out[:, :, 3:4] > 1e-7,
    )
    return Image.fromarray(np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8)), flipped


def transform_weapon(image: Image.Image, source_pivot: np.ndarray, source_tip: np.ndarray,
                     target_pivot: np.ndarray, target_palm: np.ndarray,
                     target_tip: np.ndarray) -> Image.Image:
    source_angle = math.atan2(source_tip[1] - source_pivot[1], source_tip[0] - source_pivot[0])
    target_angle = math.atan2(target_tip[1] - target_palm[1], target_tip[0] - target_palm[0])
    angle = target_angle - source_angle
    cosine, sine = math.cos(angle), math.sin(angle)
    sx, sy = source_pivot
    tx, ty = target_pivot
    affine = (
        cosine, sine, sx - cosine * tx - sine * ty,
        -sine, cosine, sy + sine * tx - cosine * ty,
    )
    return image.convert("RGBA").transform(
        (CELL, CELL), Image.Transform.AFFINE, affine,
        resample=Image.Resampling.BICUBIC,
    )


def contact_sheet(frames: list[Image.Image], path: Path) -> None:
    sheet = Image.new("RGBA", (CELL * 4, CELL * 4), (*BACKGROUND, 255))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        x, y = (index % 4) * CELL, (index // 4) * CELL
        sheet.alpha_composite(frame, (x, y))
        draw.text((x + 5, y + 4), f"{index:02d}", fill=(20, 20, 20))
    sheet.convert("RGB").save(path)


def write_gif(frames: list[Image.Image], durations: list[int], path: Path,
              final_hold_ms: int) -> int:
    held = list(durations)
    held[-1] = max(held[-1], final_hold_ms)
    total_units = round(sum(held) / 10)
    units = [duration // 10 for duration in held]
    remainder = total_units - sum(units)
    order = sorted(range(len(held)), key=lambda index: (-(held[index] % 10), index))
    for index in order[:remainder]:
        units[index] += 1
    encoded = [unit * 10 for unit in units]
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (CELL, CELL), (*BACKGROUND, 255))
        canvas.alpha_composite(frame)
        canvases.append(canvas.convert("RGB"))
    palette_source = Image.new("RGB", (CELL, CELL * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * CELL))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
               for frame in canvases]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=encoded,
                    disposal=2, optimize=False)
    return sum(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-root", type=Path, required=True,
                        help="Research template directory containing pose-guides.json and SE layers")
    parser.add_argument("--motion-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--root-x", type=int, default=160)
    parser.add_argument("--root-y", type=int, default=264)
    args = parser.parse_args()

    guide_data = json.loads((args.template_root / "pose-guides.json").read_text(encoding="utf-8"))
    source_guide = guide_data["guides"]["SE"]
    image_size = int(guide_data["canvas"][0])
    if image_size != CELL:
        parser.error(f"research source master must use {CELL}px cells")
    motion = json.loads(args.motion_manifest.read_text(encoding="utf-8"))
    frames_data = motion.get("frames", [])
    if len(frames_data) != 16:
        parser.error("expected the reviewed 16-frame Rokoko motion manifest")
    timeline_path = args.motion_manifest.parent / "motion-timeline.json"
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    durations_by_source = {
        int(frame["source_frame"]): int(frame["duration_ms"])
        for frame in timeline.get("frames", [])
    }
    if len(durations_by_source) != 16:
        parser.error("the sibling motion timeline must contain all 16 source-frame durations")
    source_names, source = source_points(source_guide)
    triangulation = Delaunay(source).simplices
    layers = {
        name: Image.open(args.template_root / "SE" / f"{name}.png").convert("RGBA")
        for name in LAYERS
    }
    if any(layer.size != (CELL, CELL) for layer in layers.values()):
        parser.error("all source research layers must be registered 320x320 canvases")
    source_weapon_pivot = np.asarray(source_guide["hand_R"], dtype=np.float64)
    source_weapon_tip = np.asarray(source_guide["weapon_tip"], dtype=np.float64)
    source_weapon_length = float(np.linalg.norm(source_weapon_tip - source_weapon_pivot))

    output_frames: list[Image.Image] = []
    audits: list[dict[str, object]] = []
    layer_root = args.output_root / "layers"
    frames_root = args.output_root / "master/frames"
    frames_root.mkdir(parents=True, exist_ok=True)
    for layer in LAYERS:
        (layer_root / layer / "frames").mkdir(parents=True, exist_ok=True)

    for index, record in enumerate(frames_data):
        coordinate_space = motion.get("body_landmark_coordinate_space", [1024, 1024])
        image_size = int(coordinate_space[0])
        scale = CELL / image_size
        targets, root_shift = target_points(record, image_size, source_guide,
                                            args.root_x, args.root_y)
        root_dx = root_shift["root_dx_px"]
        root_dy = root_shift["floor_dy_px"]
        audit = {
            "sprite_frame": index,
            "source_frame": int(record["source_frame"]),
            "root_dx_px": round(root_dx, 3),
            "floor_dy_px": round(root_dy, 3),
            "target_landmarks_xy": {name: [round(float(v), 3) for v in targets[4 + i]]
                                    for i, name in enumerate(BODY_POINTS)},
            "flipped_triangles_by_layer": {},
        }

        warped: dict[str, Image.Image] = {}
        for name in LAYERS:
            if name == "Weapon":
                continue
            warped[name], flipped = warp_rgba(layers[name], source, targets, triangulation)
            audit["flipped_triangles_by_layer"][name] = flipped

        target_hand = targets[4 + BODY_POINTS.index("hand_R")]
        target_palm = np.asarray(record["right_hand_palm_xy_px"], dtype=np.float64) * scale
        target_tip = np.asarray(record["proxy_tip_xy_px"], dtype=np.float64) * scale
        target_palm += (root_dx, root_dy)
        target_tip += (root_dx, root_dy)
        warped["Weapon"] = transform_weapon(
            layers["Weapon"], source_weapon_pivot, source_weapon_tip,
            target_hand, target_palm, target_tip,
        )

        composite = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        for name in LAYERS:
            composite.alpha_composite(warped[name])
        before_root_y, _ = find_foot_baseline(composite)
        pixel_root_correction = args.root_y - before_root_y
        if pixel_root_correction:
            corrected_layers: dict[str, Image.Image] = {}
            for name, layer in warped.items():
                corrected = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
                corrected.alpha_composite(layer, (0, pixel_root_correction))
                corrected_layers[name] = corrected
            warped = corrected_layers
            composite = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
            for name in LAYERS:
                composite.alpha_composite(warped[name])
        output_root_y, _ = find_foot_baseline(composite)
        if output_root_y != args.root_y:
            raise RuntimeError(
                f"frame {index} footwear root is y={output_root_y}; expected {args.root_y}"
            )
        for name in LAYERS:
            warped[name].save(layer_root / name / "frames" / f"se_{index:02d}.png")
        composite.save(frames_root / f"se_{index:02d}.png")
        output_frames.append(composite)
        target_hand = targets[4 + BODY_POINTS.index("hand_R")]
        target_palm = np.asarray(record["right_hand_palm_xy_px"], dtype=np.float64) * scale
        target_tip = np.asarray(record["proxy_tip_xy_px"], dtype=np.float64) * scale
        target_palm += (root_dx, root_dy + pixel_root_correction)
        target_tip += (root_dx, root_dy + pixel_root_correction)
        axis = target_tip - target_palm
        axis_length = max(float(np.linalg.norm(axis)), 1e-6)
        blade_tip = target_hand + axis / axis_length * source_weapon_length
        blade_tip[1] += pixel_root_correction
        audit["weapon_path"] = {
            "pivot_xy": [round(float(target_hand[0]), 3),
                         round(float(target_hand[1] + pixel_root_correction), 3)],
            "proxy_palm_xy": [round(float(v), 3) for v in target_palm],
            "proxy_tip_xy": [round(float(v), 3) for v in target_tip],
            "blade_tip_xy": [round(float(v), 3) for v in blade_tip],
            "authored_blade_length_px": round(source_weapon_length, 3),
            "blade_angle_degrees": round(math.degrees(math.atan2(axis[1], axis[0])), 3),
        }
        audit["output_alpha_bbox_xyxy"] = list(composite.getchannel("A").getbbox() or ())
        audit["foot_baseline_before_root_correction_y_px"] = before_root_y
        audit["foot_root_correction_px"] = pixel_root_correction
        audit["output_foot_baseline_y_px"] = output_root_y
        audits.append(audit)

    review = args.output_root / "review"
    review.mkdir(parents=True, exist_ok=True)
    contact_sheet(output_frames, review / "basicattack-se-research-warp-contact-4x4.png")
    durations = [durations_by_source[int(frame["source_frame"])] for frame in frames_data]
    gif_duration = write_gif(output_frames, durations,
                             review / "basicattack-se-research-warp-one-shot.gif",
                             int(motion.get("recovery_hold_ms", 300)))
    payload = {
        "status": "REVIEW_ONLY_RESEARCH_LAYER_WARP; NOT_PRODUCTION_APPROVED",
        "method_reference": "research/modular-sprites-full-body-2026-10-11 candidate-06 fixed-source-triangulation and rigid weapon pivot",
        "source_template": "research candidate-06 SE modular-master layers; owner approval on source motion candidate remains NOT_APPROVED",
        "motion_manifest": str(args.motion_manifest.resolve()),
        "motion_timeline": str(timeline_path.resolve()),
        "root_xy": [args.root_x, args.root_y],
        "shared_source_scale": 1.0,
        "weapon_transform": "preserve authored blade length; rotate about source hand_R pivot to projected Rokoko right-hand axis",
        "playback": {
            "frame_count": len(output_frames),
            "source_duration_ms": sum(durations),
            "gif_duration_ms_with_recovery_hold": gif_duration,
            "gif_loop_extension": False,
        },
        "frames": audits,
        "limitations": [
            "The source research pose/action is not used; only its internal cutout template and fixed-topology deformation method are referenced.",
            "This is one SE view. The cape remains fused in the source Outfit layer and BackAccessory is empty.",
            "Triangle folds, face/hand fidelity, foot contacts, sword occlusion, and owner art approval still require review.",
        ],
    }
    (review / "basicattack-se-research-warp-provenance.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "contact": str((review / "basicattack-se-research-warp-contact-4x4.png").resolve()),
        "gif": str((review / "basicattack-se-research-warp-one-shot.gif").resolve()),
        "frames": len(output_frames),
        "flipped_triangles_total": sum(sum(frame["flipped_triangles_by_layer"].values()) for frame in audits),
        "gif_duration_ms": gif_duration,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
