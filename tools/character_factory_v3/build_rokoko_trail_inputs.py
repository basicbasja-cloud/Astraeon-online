#!/usr/bin/env python3
"""Register the iteration-22 sword-path audit to selected painted guide frames.

This prepares the 320px timeline and pose-audit schema consumed by
paint_rokoko_trail_from_blade_path.py. Sword angle/pivot follow the research
IK audit, while the current Blender guide supplies face protection landmarks.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def interpolate_weapon_path(frames: list[dict[str, object]], source_frame: float) -> dict[str, object]:
    exact = [frame for frame in frames if math.isclose(float(frame["source_frame"]), source_frame, abs_tol=1e-5)]
    if exact:
        result = dict(exact[0]["weapon_path"])
        result["source_frame"] = source_frame
        return result
    earlier = [frame for frame in frames if float(frame["source_frame"]) < source_frame]
    later = [frame for frame in frames if float(frame["source_frame"]) > source_frame]
    if not earlier or not later:
        raise ValueError(f"no research blade-path samples bracket source frame {source_frame:g}")
    before = max(earlier, key=lambda frame: float(frame["source_frame"]))
    after = min(later, key=lambda frame: float(frame["source_frame"]))
    a = float(before["source_frame"])
    b = float(after["source_frame"])
    t = (source_frame - a) / (b - a)
    p0 = before["weapon_path"]
    p1 = after["weapon_path"]
    pivot = [float(p0["pivot_xy"][i]) * (1 - t) + float(p1["pivot_xy"][i]) * t for i in range(2)]
    angle0 = float(p0["blade_angle_degrees"])
    angle1 = float(p1["blade_angle_degrees"])
    angle_delta = (angle1 - angle0 + 180.0) % 360.0 - 180.0
    angle = angle0 + angle_delta * t
    length = float(p0.get("source_authored_blade_length_px", math.dist(p0["pivot_xy"], p0["blade_tip_xy"])))
    tip = [pivot[0] + length * math.cos(math.radians(angle)),
           pivot[1] + length * math.sin(math.radians(angle))]
    return {
        "source_frame": source_frame,
        "pivot_xy": pivot,
        "blade_tip_xy": tip,
        "blade_angle_degrees": angle,
        "source_authored_blade_length_px": length,
        "interpolated_from_source_frames": [a, b],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=Path, required=True)
    parser.add_argument("--guide-manifest", type=Path, required=True)
    parser.add_argument("--research-audit", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--canvas-size", type=float, required=True)
    parser.add_argument("--root-x", type=float, required=True)
    parser.add_argument("--root-y", type=float, required=True)
    parser.add_argument("--guide-scale", type=float, required=True)
    parser.add_argument("--cell-size", type=int, default=320)
    args = parser.parse_args()

    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    guide = json.loads(args.guide_manifest.read_text(encoding="utf-8"))
    research = json.loads(args.research_audit.read_text(encoding="utf-8"))
    guide_by_source = {float(item["source_frame"]): item for item in guide["frames"]}
    research_frames = research["frames"]
    research_root = research["root_xy"]
    target_root = [args.root_x * args.cell_size / args.canvas_size,
                   args.root_y * args.cell_size / args.canvas_size]
    weapon_shift = [target_root[i] - float(research_root[i]) for i in range(2)]
    gif_delays = timeline.get("gif_delays_ms", [])
    frame_data = []
    compatible_timeline = {
        "status": timeline.get("status", "REVIEW_ONLY_NOT_APPROVED"),
        "recovery_hold_ms": timeline.get("final_recovery_hold_ms", 300),
        "source_fps": timeline["source_fps"],
        "frame_count": timeline["frame_count"],
        "one_shot": True,
        "frames": [],
    }
    for index, item in enumerate(timeline["frames"]):
        source_frame = float(item["source_frame"])
        guide_frame = guide_by_source[source_frame]
        landmarks = guide_frame["body_landmarks_xy_px"]
        guide_root = [
            (float(landmarks["foot_R"][0]) + float(landmarks["foot_L"][0])) / 2.0,
            (float(landmarks["foot_R"][1]) + float(landmarks["foot_L"][1])) / 2.0,
        ]

        def map_landmark(name: str) -> list[float]:
            point = landmarks[name]
            ratio = args.guide_scale * args.cell_size / args.canvas_size
            return [round(target_root[0] + (float(point[0]) - guide_root[0]) * ratio, 4),
                    round(target_root[1] + (float(point[1]) - guide_root[1]) * ratio, 4)]

        weapon = interpolate_weapon_path(research_frames, source_frame)
        weapon["pivot_xy"] = [round(float(weapon["pivot_xy"][i]) + weapon_shift[i], 4) for i in range(2)]
        weapon["blade_tip_xy"] = [round(float(weapon["blade_tip_xy"][i]) + weapon_shift[i], 4) for i in range(2)]
        duration = int(gif_delays[index]) if index < len(gif_delays) else round(float(item["duration_ms_exact"]) / 10) * 10
        compatible_timeline["frames"].append({
            "sprite_frame": index,
            "source_frame": source_frame,
            "duration_ms": duration,
        })
        frame_data.append({
            "sprite_frame": index,
            "source_frame": source_frame,
            "weapon_path": weapon,
            "landmarks_xy": {"head": map_landmark("head")},
            "pixel_root_correction_y": 0,
            "registration": {
                "research_root_xy": research_root,
                "target_root_xy": target_root,
                "weapon_shift_xy": [round(value, 4) for value in weapon_shift],
                "weapon_path_source": "iteration-22 research IK audit; source frame interpolated only when absent",
                "head_exclusion_source": "iteration-22 Blender guide landmarks transformed to the current painted-cell root",
            },
        })

    audit_payload = {
        "status": "REVIEW_ONLY_WEAPONLIGHT_GUIDE_REGISTERED",
        "motion_source": guide.get("source_title"),
        "root_xy": target_root,
        "source_research_audit": str(args.research_audit),
        "weapon_registration": "Rokoko angle and research IK hand pivot retained; translated from research root to padded iteration-23 root",
        "frame_count": len(frame_data),
        "frames": frame_data,
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "weaponlight-timeline.json").write_text(
        json.dumps(compatible_timeline, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_root / "weaponlight-pose-audit.json").write_text(
        json.dumps(audit_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "frames": len(frame_data),
        "target_root_xy": target_root,
        "weapon_shift_xy": weapon_shift,
        "timeline": str(args.output_root / "weaponlight-timeline.json"),
        "pose_audit": str(args.output_root / "weaponlight-pose-audit.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
