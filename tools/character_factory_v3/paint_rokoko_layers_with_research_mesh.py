#!/usr/bin/env python3
"""Bake Rokoko attack deltas into the researched, limb-aware Swordsman layers.

The guide owns the motion, while the research donor owns the painted surface
construction. The source art is fitted toward the first guide pose; later
native frames use screen-space Rokoko deltas and constrained two-bone IK.
This is an offline review render, not production approval.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


CELL = 320
GRID = 4
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BODY_POINTS = [
    "head", "neck", "waist",
    "shoulder_R", "elbow_R", "hand_R",
    "shoulder_L", "elbow_L", "hand_L",
    "hip_R", "knee_R", "foot_R",
    "hip_L", "knee_L", "foot_L",
]
LAYERS = ["BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "Headgear"]
DRAW_ORDER = ["BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "Headgear"]
BG = (235, 235, 235)


def load_painter(source_file: Path, template_root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("research_painted_surface", source_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load research surface source: {source_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE = template_root
    return module


def vector(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def source_frame_number(value: Any) -> int | float:
    frame = round(float(value), 4)
    return int(frame) if frame.is_integer() else frame


def solve_two_bone(start: np.ndarray, wanted_joint: np.ndarray, wanted_end: np.ndarray,
                   first_length: float, second_length: float,
                   previous_joint: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    """Keep projected segment lengths bounded and shift an unreachable endpoint minimally."""
    delta = wanted_end - start
    distance = float(np.linalg.norm(delta))
    if distance < 1e-6:
        direction = wanted_joint - start
        direction_length = float(np.linalg.norm(direction))
        direction = direction / direction_length if direction_length > 1e-6 else np.array([1.0, 0.0])
    else:
        direction = delta / distance

    minimum_reach = abs(first_length - second_length) + 1e-4
    maximum_reach = first_length + second_length - 1e-4
    solved_distance = min(max(distance, minimum_reach), maximum_reach)
    end = start + direction * solved_distance
    error = float(np.linalg.norm(end - wanted_end))
    if solved_distance < 1e-6:
        return start + np.array([0.0, -first_length]), end, error

    along = (first_length * first_length - second_length * second_length
             + solved_distance * solved_distance) / (2.0 * solved_distance)
    height = math.sqrt(max(0.0, first_length * first_length - along * along))
    perpendicular = np.array([-direction[1], direction[0]])
    center = start + direction * along
    option_a = center + perpendicular * height
    option_b = center - perpendicular * height
    # IK has two valid solutions. Picking the nearest target independently can
    # switch the elbow/knee to the other side of the limb between frames. Prefer
    # the nearest point to the prior frame so the bend follows the projected
    # motion continuously, including when the source limb turns through depth.
    reference = wanted_joint if previous_joint is None else previous_joint
    joint = option_a if np.linalg.norm(option_a - reference) <= np.linalg.norm(option_b - reference) else option_b
    return joint, end, error


def build_targets(source_guide: dict[str, Any], motion_frames: list[dict[str, Any]],
                  support_root_y: float, limb_scale: float,
                  initial_pose_fit: float, limb_ratio_min: float,
                  limb_ratio_max: float) -> tuple[list[np.ndarray], list[dict[str, Any]]]:
    source_base = {name: vector(source_guide[name]) for name in BODY_POINTS}
    first = motion_frames[0]["body_landmarks_xy_px"]
    scale = CELL / 1024.0
    motion_waist = vector(first["waist"])
    source_waist = source_base["waist"]
    base = {
        name: source_base[name] * (1.0 - initial_pose_fit)
        + (source_waist + (vector(first[name]) - motion_waist) * scale) * initial_pose_fit
        for name in BODY_POINTS
    }
    targets: list[np.ndarray] = []
    audits: list[dict[str, Any]] = []
    support_side: str | None = None
    previous_solved_joints: dict[str, np.ndarray] = {}
    # Source-screen segment lengths change as limbs turn in depth. Keep their
    # foreshortening smooth and bounded; unreachable endpoints are shifted by
    # IK and the resulting miss is recorded rather than hiding the distortion.

    for frame_index, frame in enumerate(motion_frames):
        raw = frame["body_landmarks_xy_px"]
        target = {
            name: base[name] + (vector(raw[name]) - vector(first[name])) * scale
            for name in BODY_POINTS
        }

        desired = {name: point.copy() for name, point in target.items()}
        clamped: list[str] = []
        endpoint_errors: dict[str, float] = {}
        for proximal, joint, distal in [
            ("shoulder_R", "elbow_R", "hand_R"),
            ("shoulder_L", "elbow_L", "hand_L"),
            ("hip_R", "knee_R", "foot_R"),
            ("hip_L", "knee_L", "foot_L"),
        ]:
            base_first = float(np.linalg.norm(base[joint] - base[proximal]))
            base_second = float(np.linalg.norm(base[distal] - base[joint]))
            projected_first = float(np.linalg.norm(desired[joint] - desired[proximal]))
            projected_second = float(np.linalg.norm(desired[distal] - desired[joint]))
            ratio_first = float(np.clip(projected_first / max(base_first, 1e-6) * limb_scale,
                                        limb_ratio_min, limb_ratio_max))
            ratio_second = float(np.clip(projected_second / max(base_second, 1e-6) * limb_scale,
                                         limb_ratio_min, limb_ratio_max))
            rest_first = base_first * ratio_first
            rest_second = base_second * ratio_second
            new_joint, new_distal, endpoint_error = solve_two_bone(
                target[proximal], target[joint], target[distal], rest_first, rest_second,
                previous_solved_joints.get(joint),
            )
            if np.linalg.norm(new_joint - desired[joint]) > 0.5:
                clamped.append(joint)
            if endpoint_error > 0.5:
                clamped.append(distal)
            endpoint_errors[distal] = round(endpoint_error, 3)
            target[joint] = new_joint
            target[distal] = new_distal
            previous_solved_joints[joint] = new_joint.copy()

        # Choose the support foot once and keep it as the ground anchor for the
        # whole clip; never switch the root between feet from frame to frame.
        if support_side is None:
            support_side = "R" if target["foot_R"][1] >= target["foot_L"][1] else "L"
        support_y = float(target[f"foot_{support_side}"][1])
        root_dy = support_root_y - support_y
        # The source waist is intentionally three pixels left of the entity
        # root. Preserve that authored registration while removing motion drift.
        root_dx = float(base["waist"][0]) - float(target["waist"][0])
        for name in BODY_POINTS:
            target[name] += (root_dx, root_dy)

        targets.append(np.asarray([target[name] for name in BODY_POINTS]))
        segment_pairs = [
            ("shoulder_R", "elbow_R"), ("elbow_R", "hand_R"),
            ("shoulder_L", "elbow_L"), ("elbow_L", "hand_L"),
            ("hip_R", "knee_R"), ("knee_R", "foot_R"),
            ("hip_L", "knee_L"), ("knee_L", "foot_L"),
        ]
        audits.append({
            "sprite_frame": frame_index,
            "source_frame": source_frame_number(frame["source_frame"]),
            "root_shift_xy_px": [round(root_dx, 3), round(root_dy, 3)],
            "length_limited_joints": clamped,
            "segment_length_ratios": {
                f"{start}-{end}": round(
                    float(np.linalg.norm(target[end] - target[start])) /
                    max(float(np.linalg.norm(base[end] - base[start])), 1e-6), 4
                )
                for start, end in segment_pairs
            },
            "landmarks_xy": {
                name: [round(float(component), 3) for component in target[name]]
                for name in BODY_POINTS
            },
            "support_foot": support_side,
            "endpoint_reach_error_px": endpoint_errors,
        })
    return targets, audits


def make_point_sets(guide: dict[str, Any], target_body: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    names = ["head", "neck", "waist", "shoulder_R", "elbow_R", "hand_R",
             "shoulder_L", "elbow_L", "hand_L", "hip_R", "knee_R", "foot_R",
             "hip_L", "knee_L", "foot_L"]
    corners = np.asarray([[0, 0], [CELL - 1, 0], [CELL - 1, CELL - 1], [0, CELL - 1]],
                         dtype=np.float64)
    source_body = np.asarray([guide[name] for name in names], dtype=np.float64)
    source_support = np.asarray([
        [guide["head"][0] + dx, guide["head"][1] + dy]
        for dx, dy in [(-30, -28), (30, -28), (-30, 16), (30, 16)]
    ], dtype=np.float64)
    head_delta = target_body[names.index("head")] - source_body[names.index("head")]
    target_support = source_support + head_delta
    return np.vstack([corners, source_body, source_support]), np.vstack([
        corners, target_body, target_support
    ])


def composite_layers(layers: dict[str, Image.Image]) -> Image.Image:
    result = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    for name in DRAW_ORDER:
        result.alpha_composite(layers[name])
    return result


def shift(image: Image.Image, dy: int) -> Image.Image:
    if not dy:
        return image
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.alpha_composite(image, (0, dy))
    return result


def clean_source_red_fringe(image: Image.Image) -> tuple[Image.Image, int]:
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3] > 0
    fringe = (alpha & (rgb[:, :, 0] >= 180) & (rgb[:, :, 1] <= 95)
              & (rgb[:, :, 2] <= 95) & (rgb[:, :, 0] - rgb[:, :, 1] >= 95)
              & (rgb[:, :, 0] - rgb[:, :, 2] >= 95))
    count = int(fringe.sum())
    rgba[fringe, 3] = 0
    rgba[fringe, :3] = 0
    return Image.fromarray(rgba), count


def remove_skin_below_root(image: Image.Image, root_y: int,
                           covering_layer: Image.Image | None = None) -> tuple[Image.Image, int]:
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgb = rgba[:, :, :3].astype(np.int16)
    y, _ = np.mgrid[:rgba.shape[0], :rgba.shape[1]]
    alpha = rgba[:, :, 3] > 0
    skin = ((rgb[:, :, 0] > rgb[:, :, 1] * 1.15)
            & (rgb[:, :, 1] > rgb[:, :, 2] * 1.12)
            & (rgb[:, :, 0] > 105))
    uncovered = np.ones_like(alpha)
    if covering_layer is not None:
        # Antialiased cloth edges with a few nonzero alpha values are not opaque
        # enough to hide the bare body underneath.
        uncovered = np.asarray(covering_layer.convert("RGBA"))[:, :, 3] < 128
    # Bare-body pixels just outside boot silhouettes create a skin-colored tab
    # under the heel. Restrict the cleanup to the lowest 24 px of the sprite,
    # keep skin covered by the boot/outfit, and leave the footwear pixels intact.
    stray = alpha & skin & uncovered & (y >= root_y - 24)
    count = int(stray.sum())
    rgba[stray, 3] = 0
    rgba[stray, :3] = 0
    return Image.fromarray(rgba), count


def save_contact(frames: list[Image.Image], path: Path) -> None:
    rows = math.ceil(len(frames) / GRID)
    sheet = Image.new("RGBA", (CELL * GRID, CELL * rows), (*BG, 255))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        x, y = (index % GRID) * CELL, (index // GRID) * CELL
        sheet.alpha_composite(frame, (x, y))
        draw.text((x + 6, y + 5), f"{index:02d}", fill=(20, 20, 20))
    sheet.convert("RGB").save(path)


def save_gif(frames: list[Image.Image], durations: list[int], path: Path,
             final_hold_ms: int, scale: int = 3) -> int:
    values = list(durations)
    values[-1] = max(values[-1], final_hold_ms)
    units = [int(value) // 10 for value in values]
    target = round(sum(values) / 10)
    remaining = target - sum(units)
    order = sorted(range(len(values)), key=lambda i: (-(values[i] % 10), i))
    for index in order[:remaining]:
        units[index] += 1
    delays = [unit * 10 for unit in units]
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (CELL, CELL), (*BG, 255))
        canvas.alpha_composite(frame)
        canvases.append(canvas.resize((CELL * scale, CELL * scale), Image.Resampling.LANCZOS).convert("RGB"))
    palette_source = Image.new("RGB", (CELL * scale, CELL * scale * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * CELL * scale))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE)
               for frame in canvases]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=delays,
                    disposal=2, optimize=False)
    return sum(delays)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--research-source", type=Path, required=True)
    parser.add_argument("--motion-manifest", type=Path, required=True)
    parser.add_argument("--motion-timeline", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--root-x", type=float, default=160.0)
    parser.add_argument("--support-root-y", type=float, default=262.0)
    parser.add_argument("--pixel-root-y", type=int, default=264)
    parser.add_argument("--limb-length-scale", type=float, default=1.0,
                        help="Scale multiplier for projected segment lengths before the ratio bounds.")
    parser.add_argument("--limb-ratio-min", type=float, default=0.35,
                        help="Minimum projected 2D segment length as a fraction of source art.")
    parser.add_argument("--limb-ratio-max", type=float, default=1.40,
                        help="Maximum projected 2D segment length as a fraction of source art.")
    parser.add_argument("--initial-pose-fit", type=float, default=0.75,
                        help="Blend the source pose toward the measured first Rokoko pose (0..1).")
    args = parser.parse_args()

    guides = json.loads((args.template_root / "pose-guides.json").read_text(encoding="utf-8"))
    source_guide = guides["guides"]["SE"]
    motion = json.loads(args.motion_manifest.read_text(encoding="utf-8"))
    timeline = json.loads(args.motion_timeline.read_text(encoding="utf-8"))
    records = motion.get("frames", [])
    timeline_frames = timeline.get("frames", [])
    if len(records) < 2 or len(timeline_frames) != len(records):
        parser.error("expected matching Rokoko motion and timeline frames")
    if any(not math.isclose(float(records[i]["source_frame"]),
                            float(timeline_frames[i]["source_frame"]), abs_tol=1e-5)
           for i in range(len(records))):
        parser.error("motion manifest and timeline source frames do not match")
    source_frames = [float(frame["source_frame"]) for frame in records]
    if source_frames != sorted(set(source_frames)):
        parser.error("Rokoko source frames must be unique and in ascending order")
    if not (0.8 <= args.limb_length_scale <= 1.4):
        parser.error("limb length scale must be in [0.8, 1.4]")
    if not (0.0 < args.limb_ratio_min <= 1.0 <= args.limb_ratio_max):
        parser.error("projected limb ratio bounds must enclose 1.0 and stay positive")
    if not (0.0 <= args.initial_pose_fit <= 1.0):
        parser.error("initial pose fit must be in [0, 1]")

    source_module = args.research_source.resolve()
    if not source_module.is_file():
        parser.error(f"missing adapted research source: {source_module}")
    leg_template = args.template_root / "male/leg-templates/SE.png"
    if not leg_template.is_file():
        parser.error(f"missing same-view researched leg template: {leg_template}")
    painter = load_painter(source_module, args.template_root.resolve())
    template_layers = {
        name: Image.open(args.template_root / "SE" / f"{name}.png").convert("RGBA")
        for name in LAYERS
    }
    if any(layer.size != (CELL, CELL) for layer in template_layers.values()):
        parser.error("all researched source layers must be registered 320x320 canvases")

    targets, pose_audits = build_targets(source_guide, records, args.support_root_y,
                                         args.limb_length_scale, args.initial_pose_fit,
                                         args.limb_ratio_min, args.limb_ratio_max)
    unwrapped_angles = [float(records[0]["proxy_angle_degrees"])]
    for record in records[1:]:
        angle = float(record["proxy_angle_degrees"])
        angle += 360.0 * round((unwrapped_angles[-1] - angle) / 360.0)
        unwrapped_angles.append(angle)
    source_weapon_angle = math.degrees(math.atan2(
        source_guide["weapon_tip"][1] - source_guide["hand_R"][1],
        source_guide["weapon_tip"][0] - source_guide["hand_R"][0],
    ))
    source_weapon_length = float(np.linalg.norm(
        vector(source_guide["weapon_tip"]) - vector(source_guide["hand_R"])
    ))

    layer_paths = {
        name: args.output_root / "layers" / name / "frames"
        for name in LAYERS
    }
    for directory in layer_paths.values():
        directory.mkdir(parents=True, exist_ok=True)
    master_frames_dir = args.output_root / "master/frames"
    master_frames_dir.mkdir(parents=True, exist_ok=True)
    review_dir = args.output_root / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    output_frames: list[Image.Image] = []
    fixed_pixel_correction: int | None = None
    removed_red_pixels = 0
    removed_below_root_skin = 0

    for index, record in enumerate(records):
        source_points, target_points = make_point_sets(source_guide, targets[index])
        joints = {name: targets[index][BODY_POINTS.index(name)] for name in BODY_POINTS}
        sockets = {
            "root": [args.root_x, args.support_root_y],
            "head": joints["head"].tolist(),
            "hand_R": joints["hand_R"].tolist(),
            "hand_L": joints["hand_L"].tolist(),
            "back": joints["neck"].tolist(),
            "waist": joints["waist"].tolist(),
            "foot_R": joints["foot_R"].tolist(),
            "foot_L": joints["foot_L"].tolist(),
            "ankle_R": (joints["foot_R"] + np.array([0.0, -12.0])).tolist(),
            "ankle_L": (joints["foot_L"] + np.array([0.0, -12.0])).tolist(),
        }
        target_weapon_angle = unwrapped_angles[index]
        delta_angle = target_weapon_angle - source_weapon_angle
        layers: dict[str, Image.Image] = {}
        layers["BaseBody"] = painter.painted_body_motion(
            template_layers["BaseBody"], source_points, target_points, source_guide,
            sockets, "SE", "BaseBody", articulateArms=True, armBehind=False,
        )
        layers["Outfit"] = painter.painted_body_motion(
            template_layers["Outfit"], source_points, target_points, source_guide,
            sockets, "SE", "Outfit", articulateArms=True, armBehind=False,
        )
        layers["Hair"] = painter.rigid_weapon(
            template_layers["Hair"], source_guide["head"], joints["head"], 0.0,
        )
        layers["Weapon"] = painter.rigid_weapon(
            template_layers["Weapon"], source_guide["hand_R"], joints["hand_R"],
            delta_angle,
        )
        layers["BackAccessory"] = template_layers["BackAccessory"].copy()
        layers["Headgear"] = template_layers["Headgear"].copy()

        for name in LAYERS:
            layers[name], removed = clean_source_red_fringe(layers[name])
            removed_red_pixels += removed
        # Reuse the source root registration and correct only pixel rounding.
        composite = composite_layers(layers)
        from tools.character_factory_v3.prepare_basicattack_sheet import find_foot_baseline
        baseline_before, baseline_kind = find_foot_baseline(composite)
        if fixed_pixel_correction is None:
            fixed_pixel_correction = int(args.pixel_root_y) - int(baseline_before)
        pixel_correction = fixed_pixel_correction
        if pixel_correction:
            layers = {name: shift(layer, pixel_correction) for name, layer in layers.items()}
        layers["BaseBody"], removed = remove_skin_below_root(
            layers["BaseBody"], args.pixel_root_y, layers["Outfit"],
        )
        removed_below_root_skin += removed
        composite = composite_layers(layers)
        baseline_after, _ = find_foot_baseline(composite)

        for name, layer in layers.items():
            layer.save(layer_paths[name] / f"se_{index:02d}.png")
        composite.save(master_frames_dir / f"se_{index:02d}.png")
        output_frames.append(composite)

        hand = joints["hand_R"] + np.array([0.0, pixel_correction])
        blade_angle = math.radians(target_weapon_angle)
        tip = hand + source_weapon_length * np.array([math.cos(blade_angle), math.sin(blade_angle)])
        pose_audits[index].update({
            "baseline_before_pixel_correction_y": baseline_before,
            "baseline_detector": baseline_kind,
            "pixel_root_correction_y": pixel_correction,
            "baseline_after_shared_correction_y": baseline_after,
            "root_pixel_error_after_shared_correction": baseline_after - args.pixel_root_y,
            "weapon_path": {
                "pivot_xy": [round(float(hand[0]), 3), round(float(hand[1]), 3)],
                "blade_tip_xy": [round(float(tip[0]), 3), round(float(tip[1]), 3)],
                "blade_angle_degrees": round(target_weapon_angle, 3),
                "source_authored_blade_length_px": round(source_weapon_length, 3),
            },
            "output_alpha_bbox_xyxy": list(composite.getchannel("A").getbbox() or ()),
        })

    rows = math.ceil(len(output_frames) / GRID)
    contact_path = review_dir / f"basicattack-se-rokoko-research-surface-contact-{GRID}x{rows}.png"
    save_contact(output_frames, contact_path)
    durations = [int(frame["duration_ms"]) for frame in timeline_frames]
    gif_duration = save_gif(
        output_frames, durations,
        review_dir / "basicattack-se-rokoko-research-surface-one-shot.gif",
        int(timeline.get("recovery_hold_ms", 300)),
    )
    provenance = {
        "status": "REVIEW_ONLY_ROKOKO_DELTAS_RESEARCH_SURFACES; OWNER_REVIEW_PENDING",
        "motion_source": "Rokoko Mixamo sword attack, sampled by the iteration-14 Blender guide",
        "surface_method": "Adapted research candidate-06 semantic BaseBody/Outfit surface painter; right arm, legs, hair and sword are separate authored layers.",
        "source_template": "research candidate-06 SE modular master; the source action is not reused",
        "research_surface_source": str(source_module),
        "source_pose_lock": "The source SE pose is proportion-blended toward the measured first Rokoko pose, then each native source frame applies its matching normalized motion delta without sparse resampling.",
        "initial_pose_fit_ratio": args.initial_pose_fit,
        "projected_limb_ratio_bounds": [args.limb_ratio_min, args.limb_ratio_max],
        "limb_solver": "2D two-bone inverse kinematics follows source-screen joint targets with temporal bend-branch continuity and bounded, perspective-aware projected segment lengths; an endpoint moves only when the target is outside the reachable range",
        "root_policy": "in-place; support-foot screen projection is normalized to the source root and pixel baseline is corrected to root y",
        "root_xy": [args.root_x, args.pixel_root_y],
        "limb_length_scale": args.limb_length_scale,
        "shared_pixel_root_correction_y": fixed_pixel_correction,
        "removed_red_fringe_pixels": removed_red_pixels,
        "removed_skin_pixels_below_ground": removed_below_root_skin,
        "weapon_transform": "rigid authored blade; pivot follows the limb-aware painted right hand; angle delta follows the Rokoko proxy",
        "playback": {
            "frame_count": len(output_frames),
            "source_duration_ms": sum(durations),
            "gif_duration_ms_with_recovery_hold": gif_duration,
            "gif_loop_extension": False,
        "source_frame_range": [source_frame_number(source_frames[0]),
                               source_frame_number(source_frames[-1])],
            "source_sample_spacing_frames": [b - a for a, b in zip(source_frames, source_frames[1:])],
        },
        "limitations": [
            "The research source art is a review template and remains below the owner reference quality bar.",
            "The fitted source landmark pose follows the first Rokoko frame, but the donor silhouette and non-sword arm proportions do not match the source rig closely enough.",
            "Cape and outfit remain one source layer; this iteration does not reconstruct hidden cape surfaces.",
            "Only the SE direction is painted; all-direction acceptance remains open.",
        ],
        "frames": pose_audits,
    }
    (review_dir / "basicattack-se-rokoko-research-surface-provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "contact": str(contact_path.resolve()),
        "gif": str((review_dir / "basicattack-se-rokoko-research-surface-one-shot.gif").resolve()),
        "baseline_corrections": [frame["pixel_root_correction_y"] for frame in pose_audits],
        "baseline_errors_after_shared_correction": [frame["root_pixel_error_after_shared_correction"] for frame in pose_audits],
        "length_limited_frame_count": sum(bool(frame["length_limited_joints"]) for frame in pose_audits),
        "endpoint_reach_error_max_px": {
            name: round(max(frame["endpoint_reach_error_px"][name] for frame in pose_audits), 3)
            for name in pose_audits[0]["endpoint_reach_error_px"]
        },
        "segment_length_ratio_range": {
            name: [
                round(min(frame["segment_length_ratios"][name] for frame in pose_audits), 4),
                round(max(frame["segment_length_ratios"][name] for frame in pose_audits), 4),
            ]
            for name in pose_audits[0]["segment_length_ratios"]
        },
        "removed_red_fringe_pixels": removed_red_pixels,
        "removed_skin_pixels_below_ground": removed_below_root_skin,
        "gif_duration_ms": gif_duration,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
