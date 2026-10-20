#!/usr/bin/env python3
"""Render a review-only, weapon-marked sprite guide from a Rokoko Mixamo FBX.

Run with Blender 4.x/5.x:
  blender -b --python tools/character_factory_v3/render_rokoko_motion_guide.py -- \
    --fbx /path/to/SwordFight_mixamo.fbx --output /path/to/guide \
    --frames 480,482,485,487,490,492,494,496,498,499,500,502,505,508,511,514

The small sword is a projection aid built from the RightHand wrist-to-palm axis.
It is not present in the source FBX and must not be treated as a finished weapon.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image, ImageDraw


DEFAULT_FRAMES = [480, 482, 485, 487, 490, 492, 494, 496, 498, 499, 500, 502, 504, 506, 509, 511]
SOURCE_FPS = 30
IMAGE_SIZE = 1024
CELL_SIZE = 320
PROXY_LENGTH = 0.82
BACKGROUND = (242, 240, 238)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fbx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frames", default=",".join(map(str, DEFAULT_FRAMES)))
    parser.add_argument("--fps", type=int, default=SOURCE_FPS)
    parser.add_argument("--image-size", type=int, default=IMAGE_SIZE)
    parser.add_argument("--recovery-hold-ms", type=int, default=300)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    try:
        args.frames = [int(value) for value in args.frames.split(",")]
    except ValueError as error:
        parser.error(f"invalid --frames list: {error}")
    if len(args.frames) < 2 or len(set(args.frames)) != len(args.frames):
        parser.error("--frames must contain at least two unique source frames")
    if sorted(args.frames) != args.frames:
        parser.error("--frames must be in ascending source order")
    if args.fps < 1 or args.image_size < 128 or args.recovery_hold_ms < 0:
        parser.error("fps, image size, and recovery hold must be valid positive values")
    return args


def projected_pixel(scene: bpy.types.Scene, camera: bpy.types.Object, point: Vector,
                    image_size: int) -> tuple[int, int]:
    projected = world_to_camera_view(scene, camera, point)
    return (round(projected.x * image_size), round((1.0 - projected.y) * image_size))


def draw_weapon_proxy(image: Image.Image, wrist: tuple[int, int], palm: tuple[int, int],
                      tip: tuple[int, int], image_size: int) -> None:
    draw = ImageDraw.Draw(image)
    delta_x, delta_y = tip[0] - palm[0], tip[1] - palm[1]
    length = max(1.0, math.hypot(delta_x, delta_y))
    perpendicular = (-delta_y / length, delta_x / length)
    draw.line([wrist, palm], fill=(48, 30, 23, 255), width=25)
    draw.line([wrist, palm], fill=(126, 78, 45, 255), width=14)
    draw.ellipse((wrist[0] - 14, wrist[1] - 14, wrist[0] + 14, wrist[1] + 14),
                 fill=(81, 48, 32, 255), outline=(204, 157, 77, 255), width=5)
    guard_half = 0.115 * image_size / 1.82
    guard_a = (round(palm[0] + perpendicular[0] * guard_half),
               round(palm[1] + perpendicular[1] * guard_half))
    guard_b = (round(palm[0] - perpendicular[0] * guard_half),
               round(palm[1] - perpendicular[1] * guard_half))
    draw.line([guard_a, guard_b], fill=(58, 39, 28, 255), width=28)
    draw.line([guard_a, guard_b], fill=(198, 147, 69, 255), width=14)
    half_width, tip_width = 13, 4
    polygon = [
        (palm[0] + perpendicular[0] * half_width, palm[1] + perpendicular[1] * half_width),
        (tip[0] + perpendicular[0] * tip_width, tip[1] + perpendicular[1] * tip_width),
        tip,
        (tip[0] - perpendicular[0] * tip_width, tip[1] - perpendicular[1] * tip_width),
        (palm[0] - perpendicular[0] * half_width, palm[1] - perpendicular[1] * half_width),
    ]
    draw.polygon(polygon, fill=(61, 66, 77, 255), outline=(30, 33, 40, 255))
    draw.line([palm, tip], fill=(177, 193, 207, 255), width=5)
    draw.line([
        (round(palm[0] + perpendicular[0] * 7), round(palm[1] + perpendicular[1] * 7)),
        (round(tip[0] + perpendicular[0] * 2), round(tip[1] + perpendicular[1] * 2)),
    ], fill=(231, 237, 240, 255), width=2)


def main() -> None:
    args = arguments()
    output = args.output.resolve()
    frames_dir = output / "frames_1024"
    review_dir = output / "review"
    frames_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    expected_guide_names = {
        f"guide_{index:02d}_src_{frame:04d}.png" for index, frame in enumerate(args.frames)
    }
    for stale_guide in frames_dir.glob("guide_*.png"):
        if stale_guide.name not in expected_guide_names:
            stale_guide.unlink()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(
        filepath=str(args.fbx.resolve()), use_anim=True,
        automatic_bone_orientation=False, axis_forward="-Z", axis_up="Y",
    )
    scene = bpy.context.scene
    armature = next(obj for obj in bpy.data.objects if obj.type == "ARMATURE")
    hip_bone = armature.pose.bones.get("mixamorig:Hips")
    hand_bone = armature.pose.bones.get("mixamorig:RightHand")
    if hip_bone is None or hand_bone is None:
        raise RuntimeError("FBX is missing the expected Mixamo Hips or RightHand bone")
    action = armature.animation_data.action if armature.animation_data else None
    if action is None:
        raise RuntimeError("FBX contains no active source action")

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = args.image_size
    scene.render.resolution_y = args.image_size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.studio_light = "paint.sl"
    shading.color_type = "SINGLE"
    shading.single_color = (0.31, 0.37, 0.43)
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.curvature_ridge_factor = 1.25
    shading.curvature_valley_factor = 0.8

    camera_data = bpy.data.cameras.new("Rokoko_SE_ReviewCamera")
    camera = bpy.data.objects.new("Rokoko_SE_ReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2.60
    scene.camera = camera

    contact_size = CELL_SIZE
    contact = Image.new("RGB", (contact_size * 4, contact_size * math.ceil(len(args.frames) / 4)), BACKGROUND)
    draw_contact = ImageDraw.Draw(contact)
    thumbnails: list[Image.Image] = []
    records: list[dict[str, object]] = []
    for index, frame in enumerate(args.frames):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        hips = armature.matrix_world @ hip_bone.head
        target = hips + Vector((0.0, 0.0, 0.14))
        camera.location = target + Vector((2.6, -4.6, 2.1))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        scene.render.filepath = str(frames_dir / f"guide_{index:02d}_src_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)
        guide_path = Path(scene.render.filepath)
        image = Image.open(guide_path).convert("RGBA")

        wrist = armature.matrix_world @ hand_bone.head
        palm = armature.matrix_world @ hand_bone.tail
        axis = palm - wrist
        proxy_tip = palm + axis.normalized() * PROXY_LENGTH if axis.length > 1e-5 else palm
        wrist_xy = projected_pixel(scene, camera, wrist, args.image_size)
        palm_xy = projected_pixel(scene, camera, palm, args.image_size)
        tip_xy = projected_pixel(scene, camera, proxy_tip, args.image_size)
        draw_weapon_proxy(image, wrist_xy, palm_xy, tip_xy, args.image_size)
        image.save(guide_path)

        thumb = image.resize((contact_size, contact_size), Image.Resampling.LANCZOS)
        background = Image.new("RGBA", thumb.size, (*BACKGROUND, 255))
        background.alpha_composite(thumb)
        thumb_rgb = background.convert("RGB")
        thumbnails.append(thumb_rgb)
        x, y = (index % 4) * contact_size, (index // 4) * contact_size
        contact.paste(thumb_rgb, (x, y))
        draw_contact.text((x + 5, y + 4), f"{index:02d} / {frame}f", fill=(18, 18, 18))
        records.append({
            "sprite_frame": index,
            "source_frame": frame,
            "source_time_seconds": round((frame - 1) / args.fps, 6),
            "guide_png": str(guide_path.relative_to(output)),
            "right_hand_wrist_xy_px": list(wrist_xy),
            "right_hand_palm_xy_px": list(palm_xy),
            "proxy_tip_xy_px": list(tip_xy),
            "proxy_angle_degrees": round(math.degrees(math.atan2(tip_xy[1] - palm_xy[1],
                                                                   tip_xy[0] - palm_xy[0])), 3),
        })

    contact_path = review_dir / "rokoko-basicattack-se-guide-4x4.png"
    contact.save(contact_path)
    frame_durations = [round((args.frames[i + 1] - args.frames[i]) * 1000 / args.fps)
                       for i in range(len(args.frames) - 1)]
    frame_durations.append(args.recovery_hold_ms)
    gif_path = review_dir / "rokoko-basicattack-se-guide-one-shot.gif"
    thumbnails[0].save(gif_path, save_all=True, append_images=thumbnails[1:],
                       duration=frame_durations, disposal=2, optimize=False)
    timeline = {
        "action": "BasicAttack",
        "direction": "SE",
        "frame_count": len(args.frames),
        "fps": args.fps,
        "loop": False,
        "duration_ms": sum(frame_durations),
        "source_id": "swordsman_attack_v3_rokoko_01",
        "source_file": args.fbx.name,
        "source_action": action.name,
        "source_frame_range": [args.frames[0], args.frames[-1]],
        "timing_method": "source-frame spacing at source FPS with one held recovery frame",
        "recovery_hold_ms": args.recovery_hold_ms,
        "frames": [
            {
                "index": index,
                "phase": round((args.frames[index] - args.frames[0]) /
                               max(1, args.frames[-1] - args.frames[0]), 6),
                "duration_ms": frame_durations[index],
                "source_frame": args.frames[index],
                "source_time_seconds": round((args.frames[index] - 1) / args.fps, 6),
                "guide_png": records[index]["guide_png"],
            }
            for index in range(len(args.frames))
        ],
    }
    (output / "motion-timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "status": "REVIEW_GUIDE_ONLY",
        "provider": "Rokoko",
        "source_title": "Rokoko Mocap 13 Free Fight Animations",
        "source_file": args.fbx.name,
        "source_fps": args.fps,
        "source_skeleton": "Mixamo",
        "source_action": action.name,
        "source_frame_range": list(map(int, action.frame_range)),
        "sampled_source_frames": args.frames,
        "root_handling": "review camera follows Hips position while preserving the source body pose and facing rotation",
        "camera": "fixed SE three-quarter review camera; 1024px source frames and 320px contact cells",
        "weapon_guide": "review-only steel/gold proxy attached to RightHand wrist-to-palm axis; source FBX has no weapon mesh",
        "frame_durations_ms": frame_durations,
        "review_contact": str(contact_path.relative_to(output)),
        "review_gif": str(gif_path.relative_to(output)),
        "frames": records,
        "limitations": [
            "This single SE view is a motion and pose reference, not a retargeted eight-direction runtime action.",
            "The sword is a wrist-axis proxy, not an authored weapon asset.",
            "The imported continuous fight sequence is cut at the recovery before the next sword lift.",
        ],
    }
    (output / "motion-guide-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "source_frames": args.frames,
                      "duration_ms": sum(frame_durations), "contact": str(contact_path),
                      "gif": str(gif_path)}, indent=2))


if __name__ == "__main__":
    main()
