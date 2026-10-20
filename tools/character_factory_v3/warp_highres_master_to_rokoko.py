#!/usr/bin/env python3
"""Warp one high-resolution Swordsman master to fixed-camera Rokoko poses.

This is an experimental pose-lock study based on the research branch's fixed
triangulation method. One complete painted master supplies all surface pixels;
the Rokoko guide supplies the body joints and weapon axis. The output is
review-only until the mesh, continuity, and semantic cutout gates pass.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import Delaunay


BODY_POINTS = [
    "head", "neck", "waist",
    "shoulder_R", "elbow_R", "hand_R",
    "shoulder_L", "elbow_L", "hand_L",
    "hip_R", "knee_R", "foot_R",
    "hip_L", "knee_L", "foot_L",
]
WEAPON_POINTS = ["weapon_pommel", "weapon_guard", "weapon_mid", "weapon_tip"]
HEAD_POINTS = ["head_tl", "head_tr", "head_bl", "head_br"]
POSE_SEGMENTS = {
    "upper_arm_R": ("shoulder_R", "elbow_R"),
    "forearm_R": ("elbow_R", "hand_R"),
    "upper_arm_L": ("shoulder_L", "elbow_L"),
    "forearm_L": ("elbow_L", "hand_L"),
    "thigh_R": ("hip_R", "knee_R"),
    "shin_R": ("knee_R", "foot_R"),
    "thigh_L": ("hip_L", "knee_L"),
    "shin_L": ("knee_L", "foot_L"),
}
POSE_STRAIN_RANGE = (0.78, 1.12)
BACKGROUND = (235, 235, 235)


def signed_area(points: np.ndarray) -> np.ndarray:
    a, b, c = points[:, 0], points[:, 1], points[:, 2]
    return ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1])
            - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])) / 2.0


def resize_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.convert("RGBa").resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def warp_rgba(image: Image.Image, source: np.ndarray, target: np.ndarray,
              triangles: np.ndarray) -> tuple[Image.Image, int]:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float64) / 255.0
    premultiplied = rgba.copy()
    premultiplied[:, :, :3] *= premultiplied[:, :, 3:4]
    output = np.zeros_like(premultiplied)
    source_area = signed_area(source[triangles])
    target_area = signed_area(target[triangles])
    flipped = int(np.count_nonzero(source_area * target_area < -1e-4))
    height, width = rgba.shape[:2]

    for triangle_index, indices in enumerate(triangles):
        original = source[indices]
        posed = target[indices]
        x0, y0 = np.maximum(0, np.floor(posed.min(axis=0))).astype(int)
        x1, y1 = np.minimum([width - 1, height - 1], np.ceil(posed.max(axis=0))).astype(int)
        if x1 < x0 or y1 < y0 or abs(target_area[triangle_index]) < 1e-6:
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
                premultiplied[:, :, channel], coordinates[:, ::-1].T,
                order=1, mode="constant", cval=0.0,
            )
            for channel in range(4)
        ])
        ix, iy = xx.ravel()[inside], yy.ravel()[inside]
        old = output[iy, ix]
        output[iy, ix] = colors + old * (1.0 - colors[:, 3:4])

    output[:, :, :3] = np.divide(
        output[:, :, :3], output[:, :, 3:4], out=np.zeros_like(output[:, :, :3]),
        where=output[:, :, 3:4] > 1e-7,
    )
    return Image.fromarray(np.clip(np.rint(output * 255.0), 0, 255).astype(np.uint8)), flipped


def compose_points(source_landmarks: dict[str, list[float]], frame: dict[str, object],
                   coordinate_size: int, canvas_size: int, root_x: int, root_y: int,
                   support_foot: str, height_ratio: float) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    factor = canvas_size / coordinate_size
    body = frame["body_landmarks_xy_px"]
    guide = {name: np.asarray(body[name], dtype=np.float64) * factor for name in BODY_POINTS}
    guide_height = max(guide["foot_R"][1], guide["foot_L"][1]) - guide["head"][1]
    source_body_height = max(source_landmarks["foot_R"][1], source_landmarks["foot_L"][1]) - source_landmarks["head"][1]
    scale_ratio = float(guide_height * height_ratio / max(source_body_height, 1.0))

    # Scale about the fixed guide pelvis and the selected support shoe. This
    # preserves the action while keeping one entity root through the clip.
    reference = np.asarray([
        guide["waist"][0], guide[support_foot][1]
    ], dtype=np.float64)
    destination_root = np.asarray([root_x, root_y], dtype=np.float64)
    root_shift = destination_root - reference

    target_body: dict[str, np.ndarray] = {}
    for name, point in guide.items():
        target_body[name] = (point - reference) * height_ratio + destination_root

    target_hand = target_body["hand_R"]
    palm = np.asarray(frame["right_hand_palm_xy_px"], dtype=np.float64) * factor
    proxy_tip = np.asarray(frame["proxy_tip_xy_px"], dtype=np.float64) * factor
    target_palm = (palm - reference) * height_ratio + destination_root
    target_proxy_tip = (proxy_tip - reference) * height_ratio + destination_root
    weapon_axis = target_proxy_tip - target_palm
    axis_length = float(np.linalg.norm(weapon_axis))
    if axis_length < 1e-5:
        raise ValueError(f"degenerate weapon proxy axis in source frame {frame['source_frame']}")
    weapon_axis /= axis_length

    source_weapon_pivot = np.asarray(source_landmarks["hand_R"], dtype=np.float64)
    source_weapon_direction = np.asarray(source_landmarks["weapon_tip"], dtype=np.float64) - source_weapon_pivot
    source_weapon_length = float(np.linalg.norm(source_weapon_direction))
    source_weapon_direction /= max(source_weapon_length, 1e-6)

    # Keep the complete blade straight and rigid around the painted fist while
    # following the Rokoko palm-to-tip axis. Hilt details remain separate mesh
    # controls so the blade does not bend with the torso triangles.
    source_weapon_controls = {
        name: np.asarray(source_landmarks[name], dtype=np.float64)
        for name in WEAPON_POINTS
    }
    target_weapon_controls: dict[str, np.ndarray] = {}
    for name, point in source_weapon_controls.items():
        signed_distance = float(np.dot(point - source_weapon_pivot, source_weapon_direction))
        target_weapon_controls[name] = target_hand + weapon_axis * signed_distance * scale_ratio

    target_head = target_body["head"]
    source_head = np.asarray(source_landmarks["head"], dtype=np.float64)
    target_head_controls = {
        name: target_head + (np.asarray(source_landmarks[name], dtype=np.float64) - source_head)
        * scale_ratio
        for name in HEAD_POINTS
    }

    source_order = [*BODY_POINTS, *HEAD_POINTS, *WEAPON_POINTS]
    target_order = [*target_body.values(), *target_head_controls.values(), *target_weapon_controls.values()]
    source_array = np.asarray([source_landmarks[name] for name in source_order], dtype=np.float64)
    target_array = np.asarray(target_order, dtype=np.float64)
    corners = np.asarray([
        [0.0, 0.0], [canvas_size - 1.0, 0.0],
        [canvas_size - 1.0, canvas_size - 1.0], [0.0, canvas_size - 1.0],
    ])
    source = np.vstack([corners, source_array])
    target = np.vstack([corners, target_array])

    desired_angle = math.degrees(math.atan2(weapon_axis[1], weapon_axis[0]))
    metadata = {
        "root_shift_xy_px": [round(float(v), 3) for v in root_shift],
        "target_body_landmarks_xy_px": {
            name: [round(float(v), 3) for v in point] for name, point in target_body.items()
        },
        "target_weapon_pivot_xy_px": [round(float(v), 3) for v in target_hand],
        "target_weapon_tip_xy_px": [round(float(v), 3) for v in target_weapon_controls["weapon_tip"]],
        "target_weapon_angle_degrees": round(desired_angle, 3),
        "source_to_target_height_scale": round(scale_ratio, 6),
    }
    return source, target, metadata


def pose_strain(source_landmarks: dict[str, list[float]], metadata: dict[str, object],
                source_scale: float) -> dict[str, object]:
    """Measure how much each source body segment must stretch to reach a guide.

    The fixed mesh experiment can render extreme distortions even when the
    output canvas and feet are perfectly registered. Keep limb length changes
    visible as a preflight gate instead of treating a low flip count as a pose
    match. Torso proportions are reported separately because a painted sprite
    must retain its authored stylization rather than match the mannequin's
    torso length by stretching the art.
    """
    targets = metadata["target_body_landmarks_xy_px"]
    segments: dict[str, dict[str, float]] = {}
    failures: list[str] = []
    minimum, maximum = POSE_STRAIN_RANGE
    for name, (start, end) in POSE_SEGMENTS.items():
        source_a = np.asarray(source_landmarks[start], dtype=np.float64)
        source_b = np.asarray(source_landmarks[end], dtype=np.float64)
        target_a = np.asarray(targets[start], dtype=np.float64)
        target_b = np.asarray(targets[end], dtype=np.float64)
        source_length = float(np.linalg.norm(source_b - source_a) * source_scale)
        target_length = float(np.linalg.norm(target_b - target_a))
        ratio = target_length / max(source_length, 1e-6)
        segments[name] = {
            "source_length_after_shared_scale_px": round(source_length, 3),
            "target_length_px": round(target_length, 3),
            "target_to_source_ratio": round(ratio, 5),
        }
        if not minimum <= ratio <= maximum:
            failures.append(name)
    torso_source = np.linalg.norm(
        np.asarray(source_landmarks["waist"], dtype=np.float64)
        - np.asarray(source_landmarks["neck"], dtype=np.float64)
    ) * source_scale
    torso_target = float(np.linalg.norm(
        np.asarray(targets["waist"], dtype=np.float64)
        - np.asarray(targets["neck"], dtype=np.float64)
    ))
    return {
        "allowed_limb_target_to_source_ratio": [minimum, maximum],
        "segments": segments,
        "torso_neck_to_waist": {
            "source_length_after_shared_scale_px": round(float(torso_source), 3),
            "target_guide_length_px": round(torso_target, 3),
            "target_to_source_ratio": round(torso_target / max(float(torso_source), 1e-6), 5),
            "review_note": "Preserve authored torso proportions; do not stretch the sprite to match the mannequin.",
        },
        "failed_segments": failures,
        "passes_pose_strain_gate": not failures,
    }


def transform_source(image: Image.Image, landmarks: dict[str, list[float]],
                     canvas_size: int) -> tuple[Image.Image, dict[str, list[float]]]:
    width, height = image.size
    fit = min(canvas_size / width, canvas_size / height)
    new_size = (round(width * fit), round(height * fit))
    fitted = resize_rgba(image, new_size)
    offset_x = (canvas_size - new_size[0]) // 2
    offset_y = (canvas_size - new_size[1]) // 2
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas.alpha_composite(fitted, (offset_x, offset_y))
    transformed = {
        name: [round(float(point[0]) * fit + offset_x, 4),
               round(float(point[1]) * fit + offset_y, 4)]
        for name, point in landmarks.items()
    }
    return canvas, transformed


def make_comparison(frames: list[tuple[float, Image.Image, Image.Image]],
                    path: Path, canvas_size: int, coordinate_size: int,
                    root_x: int, root_y: int, support_foot: str,
                    height_ratio: float) -> None:
    panel = 320
    width = panel * 2 * len(frames)
    sheet = Image.new("RGB", (width, panel + 24), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for index, (source_frame, painted, guide) in enumerate(frames):
        x = index * panel * 2
        painted_preview = painted.resize((panel, panel), Image.Resampling.LANCZOS)
        guide_record = None
        # The guide is pre-transformed to the shared root before it reaches this function.
        guide_preview = guide.resize((panel, panel), Image.Resampling.LANCZOS)
        sheet.paste(guide_preview.convert("RGB"), (x, 0), guide_preview.getchannel("A"))
        sheet.paste(painted_preview.convert("RGB"), (x + panel, 0), painted_preview.getchannel("A"))
        draw.text((x + 4, panel + 4), f"{source_frame:g}: guide | paint", fill=(20, 20, 20))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)


def make_guide(frame: dict[str, object], guide_root: Path, canvas_size: int,
               coordinate_size: int, root_x: int, root_y: int, support_foot: str,
               height_ratio: float) -> Image.Image:
    factor = canvas_size / coordinate_size
    body = frame["body_landmarks_xy_px"]
    guide = {name: np.asarray(body[name], dtype=np.float64) * factor for name in BODY_POINTS}
    reference = np.asarray([guide["waist"][0], guide[support_foot][1]], dtype=np.float64)
    root = np.asarray([root_x, root_y], dtype=np.float64)
    scale = factor * height_ratio
    source_ref = reference / factor
    inverse = (
        1.0 / scale, 0.0, float(source_ref[0] - root_x / scale),
        0.0, 1.0 / scale, float(source_ref[1] - root_y / scale),
    )
    guide_path = guide_root / str(frame["guide_png"])
    guide_image = Image.open(guide_path).convert("RGBA")
    return guide_image.transform(
        (canvas_size, canvas_size), Image.Transform.AFFINE, inverse,
        resample=Image.Resampling.BICUBIC,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-master", type=Path, required=True)
    parser.add_argument("--source-landmarks", type=Path, required=True)
    parser.add_argument("--motion-manifest", type=Path, required=True)
    parser.add_argument("--guide-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-frames", default="480,493,499,511")
    parser.add_argument("--canvas-size", type=int, default=1280)
    parser.add_argument("--root-x", type=int, default=640)
    parser.add_argument("--root-y", type=int, default=1056)
    parser.add_argument("--support-foot", choices=("foot_R", "foot_L"), default="foot_L")
    parser.add_argument("--height-ratio", type=float, default=1.1)
    args = parser.parse_args()

    landmark_payload = json.loads(args.source_landmarks.read_text(encoding="utf-8"))
    raw_landmarks = landmark_payload["landmarks_xy_px"]
    source_image = Image.open(args.source_master).convert("RGBA")
    source_canvas, source_landmarks = transform_source(source_image, raw_landmarks, args.canvas_size)
    names = [*BODY_POINTS, *HEAD_POINTS, *WEAPON_POINTS]
    missing = [name for name in names if name not in source_landmarks]
    if missing:
        parser.error(f"missing manually marked source landmarks: {missing}")
    source_array = np.asarray([source_landmarks[name] for name in names], dtype=np.float64)
    corners = np.asarray([
        [0.0, 0.0], [args.canvas_size - 1.0, 0.0],
        [args.canvas_size - 1.0, args.canvas_size - 1.0], [0.0, args.canvas_size - 1.0],
    ])
    source_mesh = np.vstack([corners, source_array])
    triangles = Delaunay(source_mesh).simplices

    manifest = json.loads(args.motion_manifest.read_text(encoding="utf-8"))
    coordinate_size = int(manifest["body_landmark_coordinate_space"][0])
    by_frame = {float(frame["source_frame"]): frame for frame in manifest["frames"]}
    selected = [float(value.strip()) for value in args.source_frames.split(",") if value.strip()]
    if any(source_frame not in by_frame for source_frame in selected):
        parser.error("every selected source frame must exist in the Rokoko motion manifest")

    layer_root = args.output_root / "master/frames"
    layer_root.mkdir(parents=True, exist_ok=True)
    output_frames: list[tuple[float, Image.Image, Image.Image]] = []
    audits: list[dict[str, object]] = []
    for index, source_frame in enumerate(selected):
        record = by_frame[source_frame]
        source, target, metadata = compose_points(
            source_landmarks, record, coordinate_size, args.canvas_size,
            args.root_x, args.root_y, args.support_foot, args.height_ratio,
        )
        painted, flipped = warp_rgba(source_canvas, source, target, triangles)
        guide = make_guide(record, args.guide_root, args.canvas_size, coordinate_size,
                           args.root_x, args.root_y, args.support_foot, args.height_ratio)
        strain = pose_strain(source_landmarks, metadata, metadata["source_to_target_height_scale"])
        output_path = layer_root / f"source_{source_frame:g}.png"
        painted.save(output_path, optimize=True)
        frame_audit = {
            "source_frame": source_frame,
            **metadata,
            "pose_strain": strain,
            "flipped_triangle_count": flipped,
            "source_alpha_bbox": list(source_canvas.getchannel("A").getbbox() or []),
            "paint_alpha_bbox": list(painted.getchannel("A").getbbox() or []),
            "guide_alpha_bbox": list(guide.getchannel("A").getbbox() or []),
        }
        audits.append(frame_audit)
        output_frames.append((source_frame, painted, guide))

    review = args.output_root / "review"
    review.mkdir(parents=True, exist_ok=True)
    make_comparison(output_frames, review / "highres-master-guide-comparison.png",
                    args.canvas_size, coordinate_size, args.root_x, args.root_y,
                    args.support_foot, args.height_ratio)
    payload = {
        "status": "HIGHRES_FIXED_MESH_POSE_PILOT_NOT_APPROVED",
        "limb_strain_gate": "PASS" if all(frame["pose_strain"]["passes_pose_strain_gate"] for frame in audits) else "FAIL",
        "limb_strain_failed_frames": [
            frame["source_frame"] for frame in audits
            if not frame["pose_strain"]["passes_pose_strain_gate"]
        ],
        "method_reference": "research modular-sprites-full-body candidate-06 fixed-source-triangulation",
        "source_master": str(args.source_master.resolve()),
        "source_landmarks": str(args.source_landmarks.resolve()),
        "source_pose_frame": 499,
        "motion_manifest": str(args.motion_manifest.resolve()),
        "canvas_px": [args.canvas_size, args.canvas_size],
        "root_xy_px": [args.root_x, args.root_y],
        "support_foot": args.support_foot,
        "guide_height_ratio": args.height_ratio,
        "frames": audits,
        "limitations": [
            "This pilot warps a single full-character composite. Semantic BaseBody, HeadHair, Outfit, Weapon, and BackAccessory layers are not produced here.",
            "Source body landmarks are manually annotated estimates and require adjustment against the matching guide.",
            "The fixed triangulation can fold or distort the face, limbs, cape, and weapon; inspect every frame before extending this method.",
            "The image is a high-resolution paint study only; runtime, weapon-light, trail, map, and owner-review gates remain open.",
        ],
    }
    (review / "highres-master-guide-pilot-audit.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "frames": len(output_frames),
        "flipped_triangles_total": sum(frame["flipped_triangle_count"] for frame in audits),
        "comparison": str((review / "highres-master-guide-comparison.png").resolve()),
        "audit": str((review / "highres-master-guide-pilot-audit.json").resolve()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
