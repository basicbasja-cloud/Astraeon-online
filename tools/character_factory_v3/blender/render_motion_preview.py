"""Low-cost RGB-only, eight-view motion candidate preview for selection."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy


DIRECTIONS = (("S", 0), ("SW", -45), ("W", -90), ("NW", -135), ("N", -180), ("NE", -225), ("E", -270), ("SE", 45))


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-count", type=int, default=4)
    parser.add_argument("--width", type=int, default=320)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--directions", default="S,SW,W,NW,N,NE,E,SE")
    args = parser.parse_args(argv)
    scene_path = Path(args.scene).resolve()
    output_root = Path(args.output).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(scene_path))
    armature = bpy.data.objects.get("ARM_FantasyCharacter01")
    root = bpy.data.objects.get("ROOT_FantasyCharacter01")
    scene = bpy.context.scene
    if armature is None or root is None or scene.camera is None or not armature.animation_data or not armature.animation_data.action:
        raise RuntimeError("Preview scene must contain the canonical V3 rig with one retargeted action")
    action = armature.animation_data.action
    requested_directions = tuple(part.strip().upper() for part in args.directions.split(",") if part.strip())
    direction_yaws = dict(DIRECTIONS)
    if not requested_directions or any(direction not in direction_yaws for direction in requested_directions):
        raise ValueError("Preview directions must be selected from S,SW,W,NW,N,NE,E,SE")
    start, end = action.frame_range
    if args.sample_count < 2 or end <= start:
        raise ValueError("Preview needs at least two samples and an animated action")
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.width
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    output_root.mkdir(parents=True, exist_ok=True)
    frames = []
    for sample_index in range(args.sample_count):
        frame = int(round(start + (end - start) * sample_index / (args.sample_count - 1)))
        record = {"sample_index": sample_index, "frame": frame, "phase": sample_index / (args.sample_count - 1), "directions": []}
        for direction in requested_directions:
            yaw = direction_yaws[direction]
            root.rotation_euler.z = math.radians(yaw)
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            output = output_root / f"{sample_index:02d}_{direction}.png"
            scene.render.filepath = str(output.with_suffix(""))
            result = bpy.ops.render.render(write_still=True)
            if "FINISHED" not in result or not output.is_file():
                raise RuntimeError(f"Preview render failed at {frame}/{direction}: {result}")
            record["directions"].append({"direction": direction, "yaw_degrees": yaw, "file": output.name})
        frames.append(record)
    manifest = {
        "schema_version": 1,
        "motion_id": action.name.removeprefix("V3_"),
        "source_scene": str(scene_path),
        "source_action": action.name,
        "width": args.width,
        "height": args.width,
        "directions": list(requested_directions),
        "mirroring": "none",
        "frames": frames,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("V3_MOTION_PREVIEW_RENDERED", json.dumps({"motion_id": manifest["motion_id"], "directions": 8, "samples": len(frames), "output": str(output_root)}))


if __name__ == "__main__":
    main()
