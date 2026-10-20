#!/usr/bin/env python3
"""Project sampled Rokoko Mixamo hand and guide-sword axes into the SE camera.

Run through Blender (4.x/5.x) with:
  blender -b --python tools/character_factory_v3/project_rokoko_sword_path.py -- \
    --fbx /path/to/SwordFight_mixamo.fbx --output /path/to/sword-tip-path.json

The projected sword is only a review proxy built from the RightHand axis. It is
not part of the external FBX and is not a production weapon mesh.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


FRAMES = [480, 482, 485, 487, 490, 492, 494, 496, 498, 499, 500, 502, 504, 506, 509, 511]
IMAGE_SIZE = 1024
PROXY_LENGTH = 0.82


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fbx", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--image-size", type=int, default=IMAGE_SIZE)
    parser.add_argument("--proxy-length", type=float, default=PROXY_LENGTH)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(argv)


def main() -> None:
    args = arguments()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(
        filepath=str(args.fbx.resolve()),
        use_anim=True,
        automatic_bone_orientation=False,
        axis_forward="-Z",
        axis_up="Y",
    )
    scene = bpy.context.scene
    scene.render.resolution_x = args.image_size
    scene.render.resolution_y = args.image_size
    scene.render.resolution_percentage = 100
    armature = next(obj for obj in bpy.data.objects if obj.type == "ARMATURE")
    camera_data = bpy.data.cameras.new("Rokoko_SE_ReviewCamera")
    camera = bpy.data.objects.new("Rokoko_SE_ReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2.6
    scene.camera = camera

    records = []
    for index, frame in enumerate(FRAMES):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        hips = armature.matrix_world @ armature.pose.bones["mixamorig:Hips"].head
        target = hips + Vector((0, 0, 0.14))
        camera.location = target + Vector((2.6, -4.6, 2.1))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()

        hand_bone = armature.pose.bones["mixamorig:RightHand"]
        hand = armature.matrix_world @ hand_bone.head
        palm = armature.matrix_world @ hand_bone.tail
        blade_axis = (palm - hand).normalized()
        tip = palm + blade_axis * args.proxy_length

        def pixel(point: Vector) -> tuple[float, float]:
            projected = world_to_camera_view(scene, camera, point)
            return (projected.x * args.image_size, (1.0 - projected.y) * args.image_size)

        hand_px = pixel(hand)
        palm_px = pixel(palm)
        tip_px = pixel(tip)
        delta = [tip_px[0] - palm_px[0], tip_px[1] - palm_px[1]]
        records.append({
            "sprite_frame": index,
            "source_frame": frame,
            "hand_xy_px": [round(v, 3) for v in hand_px],
            "palm_xy_px": [round(v, 3) for v in palm_px],
            "proxy_tip_xy_px": [round(v, 3) for v in tip_px],
            "proxy_blade_delta_xy_px": [round(v, 3) for v in delta],
            "proxy_blade_angle_degrees": round(__import__("math").degrees(__import__("math").atan2(delta[1], delta[0])), 3),
        })

    payload = {
        "provider": "Rokoko",
        "source_file": args.fbx.name,
        "source_frames": FRAMES,
        "source_fps": 30,
        "action": "mixamorig:Reference|clip|Base_Layer",
        "camera": {"type": "orthographic", "ortho_scale": 2.6, "resolution_px": args.image_size,
                   "location_rule": "Hips + (2.6, -4.6, 2.1); target Hips + (0,0,0.14)"},
        "weapon_proxy": {"hand_bone": "mixamorig:RightHand", "length_world_units": args.proxy_length,
                         "status": "review-only axis proxy; source FBX contains no weapon mesh"},
        "records": records,
        "limitations": [
            "Projection is a motion-direction/timing reference, not a finished sprite weapon transform.",
            "The 2D painted blade may use a longer style-specific reach while preserving the projected source orientation.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve()), "frames": len(records)}, indent=2))


if __name__ == "__main__":
    main()
