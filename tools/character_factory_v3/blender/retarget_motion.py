"""Retarget a public BVH, FBX, GLB, or Blender action onto the action-free V3 rig."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


ROOT = Path(__file__).resolve().parents[3]
FACTORY = ROOT / "authoring/characters/factory-v3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def import_motion(path: Path, profile: dict, source_action_name: str | None = None) -> bpy.types.Object:
    if profile["format"] == "BVH":
        config = profile["import"]
        result = bpy.ops.import_anim.bvh(
            filepath=str(path), frame_start=1, global_scale=float(config.get("global_scale", 1.0)),
            use_fps_scale=False, update_scene_fps=False, update_scene_duration=False,
            axis_forward=config["axis_forward"], axis_up=config["axis_up"],
        )
    elif profile["format"] == "FBX":
        config = profile["import"]
        result = bpy.ops.import_scene.fbx(
            filepath=str(path), use_anim=True, automatic_bone_orientation=False,
            axis_forward=config["axis_forward"], axis_up=config["axis_up"],
        )
    elif profile["format"] in ("GLB", "GLTF"):
        result = bpy.ops.import_scene.gltf(filepath=str(path))
    elif profile["format"] == "BLEND":
        object_name = profile["source_armature"]
        with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
            if object_name not in data_from.objects:
                raise RuntimeError(f"Source armature {object_name!r} is missing from {path.name}")
            if not source_action_name or source_action_name not in data_from.actions:
                raise RuntimeError(f"Source action {source_action_name!r} is missing from {path.name}")
            data_to.objects = [object_name]
            data_to.actions = [source_action_name]
        source = next((obj for obj in data_to.objects if obj is not None), None)
        action = next((item for item in data_to.actions if item is not None), None)
        if source is None or source.type != "ARMATURE" or action is None:
            raise RuntimeError(f"Could not load armature/action {object_name!r}/{source_action_name!r}")
        bpy.context.scene.collection.objects.link(source)
        source.animation_data_create()
        source.animation_data.action = action
        return source
    else:
        raise ValueError(f"Unsupported source format: {profile['format']}")
    if "FINISHED" not in result:
        raise RuntimeError(f"Blender did not finish importing {path.name}: {result}")
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE" and obj.name != "ARM_FantasyCharacter01"]
    if not armatures:
        raise RuntimeError(f"No source armature was imported from {path.name}")
    source = armatures[-1]
    if source.animation_data is None or source.animation_data.action is None:
        actions = [action for action in bpy.data.actions if action.fcurves]
        if len(actions) != 1:
            raise RuntimeError(f"Could not identify the source action in {path.name}: {[a.name for a in actions]}")
        source.animation_data_create()
        source.animation_data.action = actions[0]
    if profile["format"] in ("GLB", "GLTF") and source_action_name:
        source_action = bpy.data.actions.get(source_action_name)
        if source_action is None:
            raise RuntimeError(f"Source action {source_action_name!r} is missing from {path.name}")
        source.animation_data_create()
        source.animation_data.action = source_action
        if source_action.slots:
            source.animation_data.action_slot = source_action.slots[0]
    return source


def matrix_rotation(matrix: Matrix) -> Quaternion:
    return matrix.to_3x3().to_quaternion().normalized()


def scaled_delta(delta: Quaternion, strength: float) -> Quaternion:
    axis, angle = delta.to_axis_angle()
    if not math.isfinite(angle) or not all(math.isfinite(value) for value in axis):
        raise ValueError("Non-finite source bone rotation")
    return Quaternion(axis, angle * strength)


def world_matrix(obj: bpy.types.Object, matrix: Matrix) -> Matrix:
    return obj.matrix_world @ matrix


def clip_fps(path: Path, source_format: str, supplied: float | None) -> float:
    if supplied:
        return float(supplied)
    if source_format == "BVH":
        header = path.read_text(encoding="utf-8", errors="replace")[:100_000]
        for line in header.splitlines():
            if line.strip().lower().startswith("frame time:"):
                frame_time = float(line.split(":", 1)[1].strip())
                if frame_time > 0:
                    return 1.0 / frame_time
        raise ValueError(f"No valid Frame Time in {path}")
    # FBX animation keys are stored as ticks; Blender's FBX reader imports them
    # at the file's declared rate. The OGA source files declare 24 FPS in the
    # FBX GlobalSettings. run.py passes that rate from the acquisition record.
    raise ValueError(f"{source_format} source_fps must come from its acquisition record")


def get_action_range(source: bpy.types.Object) -> tuple[float, float]:
    start, end = source.animation_data.action.frame_range
    if end <= start:
        raise ValueError(f"Source action has an invalid range: {start}..{end}")
    return float(start), float(end)


def height_between(armature: bpy.types.Object, top_name: str, foot_names: tuple[str, ...]) -> float:
    top = armature.data.bones.get(top_name)
    feet = [armature.data.bones.get(name) for name in foot_names]
    if top is None or any(bone is None for bone in feet):
        raise ValueError("Source/target skeleton is missing height landmarks")
    top_world = armature.matrix_world @ top.head_local
    bottom = min((armature.matrix_world @ bone.tail_local).z for bone in feet)
    height = top_world.z - bottom
    if not math.isfinite(height) or height <= 1e-6:
        raise ValueError(f"Invalid skeleton reference height: {height}")
    return float(height)


def resolve_bone_name(candidates: str | list[str], bones: bpy.types.ArmatureBones) -> str | None:
    """Resolve an explicit source-name alias list against an imported rig."""
    names = [candidates] if isinstance(candidates, str) else candidates
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise ValueError(f"Invalid source bone alias list: {candidates!r}")
    return next((name for name in names if bones.get(name) is not None), None)


def root_translation(source_root: bpy.types.PoseBone, source_obj: bpy.types.Object) -> Vector:
    return (source_obj.matrix_world @ source_root.matrix).translation.copy()


def target_bone_world(target: bpy.types.Object, bone_name: str) -> tuple[Vector, Vector]:
    pose = target.pose.bones[bone_name]
    head = target.matrix_world @ pose.head
    tail = target.matrix_world @ pose.tail
    return head, tail


def detect_contacts(samples: list[dict], fps: float) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {"left": [], "right": []}
    for side in ("left", "right"):
        poses = [item[f"toe_{side}"] for item in samples]
        contact = []
        for index, point in enumerate(poses):
            if index == 0:
                speed = 0.0
            else:
                previous = poses[index - 1]
                speed = math.dist(point, previous) * fps
            contact.append(point[2] <= 0.075 and speed <= 0.55)
        runs = []
        index = 0
        while index < len(contact):
            if not contact[index]:
                index += 1
                continue
            start = index
            while index + 1 < len(contact) and contact[index + 1]:
                index += 1
            end = index
            # Ignore one-frame noisy detections; a 30 FPS plant must persist.
            if end - start + 1 >= 2:
                runs.append({
                    "start_frame": start,
                    "end_frame": end,
                    "start_phase": round(start / max(1, len(samples) - 1), 6),
                    "end_phase": round(end / max(1, len(samples) - 1), 6),
                    "min_height": round(min(poses[item][2] for item in range(start, end + 1)), 6),
                })
            index += 1
        result[side] = runs
    return result


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rig-scene", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--source-fps", type=float)
    parser.add_argument("--source-action-name")
    parser.add_argument("--motion-id", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--output-scene", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--root-policy", choices=("in_place", "preserve_displacement"), default="in_place")
    parser.add_argument("--preview-only", action="store_true", help="Retarget only evenly spaced candidate poses; never use for production")
    parser.add_argument("--preview-frame-count", type=int, default=12)
    args = parser.parse_args(argv)

    rig_scene = Path(args.rig_scene).resolve()
    source_path = Path(args.source).resolve()
    report_path = Path(args.report).resolve()
    output_scene = Path(args.output_scene).resolve()
    profiles = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    profile = profiles["profiles"][args.profile_id]
    if profile["format"] not in ("BVH", "FBX", "GLB", "GLTF", "BLEND"):
        raise ValueError("Only explicit BVH, FBX, GLB, GLTF, and BLEND profiles are supported")
    if sha256(source_path) != args.source_sha256:
        raise ValueError("Source digest changed after provenance intake")

    bpy.ops.wm.open_mainfile(filepath=str(rig_scene))
    target = bpy.data.objects.get(profiles["canonical"]["armature"])
    root_control = bpy.data.objects.get(profiles["canonical"]["root_control"])
    if target is None or root_control is None:
        raise RuntimeError("Canonical V3 rig or root control is missing")
    if len(bpy.data.actions):
        raise RuntimeError("Canonical rig source must contain zero actions before retargeting")
    initial_objects = set(bpy.context.scene.objects)
    source = import_motion(source_path, profile, args.source_action_name)
    source_action = source.animation_data.action
    original_source_action_name = args.source_action_name or source_action.name
    source_action.name = f"SOURCE_{args.motion_id}"
    source_action_internal_name = source_action.name
    source_fps = clip_fps(source_path, profile["format"], args.source_fps)
    target_fps = int(profiles["canonical"].get("target_fps", 30))
    source_start, source_end = get_action_range(source)
    if profile.get("first_frame_is_added_rest_pose"):
        source_start += 1.0
    if source_end <= source_start:
        raise RuntimeError("Source has no motion frames after excluding its declared rest-pose frame")

    mapping = {}
    missing = []
    for target_name, source_aliases in profile["motion_bones"].items():
        source_name = resolve_bone_name(source_aliases, source.data.bones)
        if source_name is None:
            missing.append(f"{target_name}:{source_aliases}")
        else:
            mapping[target_name] = source_name
    missing_target = [target_name for target_name in mapping if target.data.bones.get(target_name) is None]
    missing_target.extend(target_name for target_name in profile["motion_bones"] if target.data.bones.get(target_name) is None)
    missing_target = sorted(set(missing_target))
    if missing or missing_target:
        raise RuntimeError(f"Mapping profile has missing bones: source={missing}, target={missing_target}")
    required_targets = {
        "root", "Hips", "Spine", "Chest", "Neck", "Head", "Clavicle.L", "UpperArm.L", "Forearm.L",
        "Hand.L", "Clavicle.R", "UpperArm.R", "Forearm.R", "Hand.R", "Thigh.L", "Shin.L", "Foot.L",
        "Thigh.R", "Shin.R", "Foot.R",
    }
    if not required_targets.issubset(mapping):
        raise RuntimeError(f"Motion profile omits required target bones: {sorted(required_targets - set(mapping))}")
    source_bone_names = sorted(b.name for b in source.data.bones)
    target_height = height_between(
        target,
        profiles["canonical"].get("height_top_bone", "Head"),
        tuple(profiles["canonical"].get("height_foot_bones", ["Toe.L", "Toe.R"])),
    )
    source_top_name = resolve_bone_name(profile.get("height_top_bone", mapping["Head"]), source.data.bones)
    source_foot_aliases = profile.get("height_foot_bones", [mapping.get("Toe.L", mapping["Foot.L"]), mapping.get("Toe.R", mapping["Foot.R"])])
    source_foot_names = tuple(resolve_bone_name(item, source.data.bones) for item in source_foot_aliases)
    if source_top_name is None or any(name is None for name in source_foot_names):
        raise RuntimeError("Source skeleton is missing its configured height landmarks")
    source_height = height_between(source, source_top_name, source_foot_names)
    scale_ratio = target_height / source_height

    source_root_name = resolve_bone_name(profile["source_root_bone"], source.data.bones)
    if source_root_name is None:
        raise RuntimeError(f"Source root bone is missing: {profile['source_root_bone']}")
    source_root_pose = source.pose.bones.get(source_root_name)
    source_root_rest = source.data.bones.get(source_root_name)
    if source_root_pose is None or source_root_rest is None:
        raise RuntimeError(f"Source root bone is missing: {source_root_name}")
    style = profile.get("stylization", {})
    time_multiplier = float(style.get("time_multiplier", 1.0))
    if not 0.5 <= time_multiplier <= 1.25:
        raise ValueError("Stylization time_multiplier must remain between 0.5 and 1.25")
    source_duration = (source_end - source_start) / source_fps
    output_count = (
        args.preview_frame_count if args.preview_only
        else max(2, int(round(source_duration * time_multiplier * target_fps)) + 1)
    )
    if output_count < 2:
        raise ValueError("Retarget output must contain at least two frames")
    source_frames = [source_start + (source_end - source_start) * index / (output_count - 1) for index in range(output_count)]

    # The output is an independent action; source FBX/BVH data is never edited.
    for pose_bone in target.pose.bones:
        pose_bone.location = (0.0, 0.0, 0.0)
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pose_bone.scale = (1.0, 1.0, 1.0)
    action = bpy.data.actions.new(f"V3_{args.motion_id}")
    target.animation_data_create()
    target.animation_data.action = action
    scene = bpy.context.scene
    scene.render.fps = target_fps
    scene.render.fps_base = 1.0
    scene.frame_start = 1
    scene.frame_end = output_count
    source_root_head0: Vector | None = None
    root_motion_positions = []
    floor_offsets = []
    pose_samples = []
    rotation_spikes = []
    previous_rotations: dict[str, Quaternion] = {}

    # All root/limb mappings are processed in canonical hierarchy order.
    target_order = [bone.name for bone in target.data.bones]
    if target_order[0] != "root":
        target_order.sort(key=lambda name: (name != "root", target.data.bones[name].parent is not None))
        # Preserve parent-before-child order by repeatedly taking ready bones.
        pending = set(target_order)
        target_order = []
        while pending:
            ready = sorted(name for name in pending if target.data.bones[name].parent is None or target.data.bones[name].parent.name in target_order)
            if not ready:
                raise RuntimeError("Canonical rig hierarchy contains a cycle")
            target_order.extend(ready)
            pending.difference_update(ready)

    for output_index, source_frame in enumerate(source_frames):
        output_frame = output_index + 1
        scene.frame_set(int(round(source_frame)))
        bpy.context.view_layer.update()
        source_root_world = world_matrix(source, source_root_pose.matrix)
        if source_root_head0 is None:
            source_root_head0 = source_root_world.translation.copy()
        source_delta_translation = source_root_world.translation - source_root_head0
        root_motion_positions.append(tuple(float(v) for v in source_delta_translation))
        if args.root_policy == "in_place":
            source_delta_translation.x = 0.0
            source_delta_translation.y = 0.0

        target_pose_by_name = target.pose.bones
        source_delta_by_target: dict[str, Quaternion] = {}
        for target_name, source_name in mapping.items():
            source_pose = source.pose.bones[source_name]
            source_rest = source.data.bones[source_name]
            pose_matrix = world_matrix(source, source_pose.matrix)
            rest_matrix = world_matrix(source, source_rest.matrix_local)
            delta = matrix_rotation(pose_matrix) @ matrix_rotation(rest_matrix).inverted()
            strength = float(style.get("rotation_strength", {}).get(target_name, style.get("rotation_strength", {}).get("default", 1.0)))
            source_delta_by_target[target_name] = scaled_delta(delta, strength)

        for target_name in target_order:
            pose_bone = target_pose_by_name[target_name]
            data_bone = target.data.bones[target_name]
            parent_data = data_bone.parent
            target_rest_world = world_matrix(target, data_bone.matrix_local)
            if parent_data:
                parent_pose_world = world_matrix(target, target_pose_by_name[parent_data.name].matrix)
                local_rest = parent_data.matrix_local.inverted() @ data_bone.matrix_local
                base_world = parent_pose_world @ local_rest
            else:
                base_world = target_rest_world.copy()
            delta = source_delta_by_target.get(target_name, Quaternion())
            target_rest_rot = matrix_rotation(target_rest_world)
            desired_world_rot = delta @ target_rest_rot
            if target_name == "root":
                desired_translation = target_rest_world.translation + source_delta_translation * scale_ratio
                base_world.translation = desired_translation
            desired_world = Matrix.Translation(base_world.translation) @ desired_world_rot.to_matrix().to_4x4()
            pose_bone.matrix = target.matrix_world.inverted() @ desired_world
            bpy.context.view_layer.update()

        # Ground correction is one shared pelvis/root offset applied before
        # contact detection. It only lifts penetration; it never randomizes zoom.
        toe_points = {}
        minimum_toe_z = float("inf")
        for side in ("L", "R"):
            head, tail = target_bone_world(target, f"Toe.{side}")
            minimum_toe_z = min(minimum_toe_z, head.z, tail.z)
            toe_points["left" if side == "L" else "right"] = tail
        floor_offset = max(0.0, -minimum_toe_z) if profiles["canonical"].get("foot_floor_correction", True) else 0.0
        if floor_offset > 0.0:
            root_pose = target_pose_by_name["root"]
            root_matrix = root_pose.matrix.copy()
            root_matrix.translation.z += floor_offset
            root_pose.matrix = root_matrix
            bpy.context.view_layer.update()
        floor_offsets.append(floor_offset)
        for side in ("L", "R"):
            head, tail = target_bone_world(target, f"Toe.{side}")
            toe_points["left" if side == "L" else "right"] = tail

        for target_name in mapping:
            pose_bone = target_pose_by_name[target_name]
            q = pose_bone.rotation_quaternion.copy()
            if not all(math.isfinite(v) for v in q):
                raise RuntimeError(f"Non-finite retarget rotation on {target_name} at output frame {output_frame}")
            if target_name in previous_rotations:
                angle = previous_rotations[target_name].rotation_difference(q).angle
                if angle > math.radians(155):
                    rotation_spikes.append({"bone": target_name, "frame": output_frame, "degrees": round(math.degrees(angle), 3)})
            previous_rotations[target_name] = q.copy()
            pose_bone.keyframe_insert(data_path="location", frame=output_frame, group=target_name)
            pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=output_frame, group=target_name)
        pose_samples.append({
            "frame": output_frame,
            "source_frame": round(source_frame, 3),
            "toe_left": tuple(float(v) for v in toe_points["left"]),
            "toe_right": tuple(float(v) for v in toe_points["right"]),
            "head_z": float((target.matrix_world @ target_pose_by_name["Head"].head).z),
            "root_xy": tuple(float(v) for v in target_pose_by_name["root"].matrix.translation[:2]),
        })
    contacts = detect_contacts(pose_samples, target_fps)
    if args.root_policy == "in_place":
        max_root_xy = max((math.hypot(*sample["root_xy"]) for sample in pose_samples), default=0.0)
    else:
        max_root_xy = max((math.hypot(sample["root_xy"][0], sample["root_xy"][1]) for sample in pose_samples), default=0.0)

    # Remove imported source-only objects and actions. The saved target scene
    # contains only this newly retargeted V3 action, never legacy V2 curves.
    for obj in list(bpy.context.scene.objects):
        if obj not in initial_objects and obj != target and obj != root_control:
            bpy.data.objects.remove(obj, do_unlink=True)
    for source_only_action in list(bpy.data.actions):
        if source_only_action != action:
            bpy.data.actions.remove(source_only_action)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    output_scene.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_scene))

    def vec_range(axis: int) -> dict[str, float]:
        values = [item[axis] for item in root_motion_positions]
        return {"min": round(min(values), 6), "max": round(max(values), 6), "net": round(values[-1] - values[0], 6)}

    report = {
        "schema_version": 1,
        "motion_id": args.motion_id,
        "status": "CANDIDATE_PREVIEW_ONLY" if args.preview_only else "RETARGETED_REQUIRES_VISUAL_REVIEW",
        "preview_only": bool(args.preview_only),
        "source": str(source_path),
        "source_sha256": args.source_sha256,
        "rig_scene_sha256": sha256(rig_scene),
        "profile_sha256": sha256(Path(args.profile).resolve()),
        "profile_id": args.profile_id,
        "retarget_script_sha256": sha256(Path(__file__).resolve()),
        "source_format": profile["format"],
        "source_action": original_source_action_name,
        "source_action_internal_name": source_action_internal_name,
        "source_fps": source_fps,
        "source_frame_range": [source_start, source_end],
        "added_first_frame_excluded": bool(profile.get("first_frame_is_added_rest_pose")),
        "source_duration_seconds": round(source_duration, 6),
        "source_skeleton_height": round(source_height, 6),
        "target_skeleton_height": round(target_height, 6),
        "root_scale_ratio": round(scale_ratio, 8),
        "root_motion_source_axes": {"x": vec_range(0), "y": vec_range(1), "z": vec_range(2)},
        "root_motion_policy": args.root_policy,
        "max_rendered_root_horizontal_excursion": round(max_root_xy, 6),
        "source_bone_mapping": mapping,
        "target_bones_unmapped": sorted(set(b.name for b in target.data.bones) - set(mapping)),
        "source_bones_unmapped": sorted(set(source_bone_names) - set(mapping.values())),
        "rotation_strength": style.get("rotation_strength", {"default": 1.0}),
        "time_multiplier": time_multiplier,
        "output_fps": target_fps,
        "output_frame_range": [1, output_count],
        "output_duration_seconds": round((output_count - 1) / target_fps, 6),
        "output_scene": str(output_scene),
        "output_scene_sha256": sha256(output_scene),
        "floor_correction": {"enabled": True, "max_lift": round(max(floor_offsets, default=0.0), 6), "mean_lift": round(sum(floor_offsets) / max(1, len(floor_offsets)), 6)},
        "foot_contacts": contacts,
        "rotation_spikes_over_155_degrees": rotation_spikes,
        "qa": {
            "finite_transforms": True,
            "mapped_required_bones": sorted(required_targets),
            "root_stable_for_in_place": args.root_policy != "in_place" or max_root_xy <= 0.001,
            "rotation_spikes_absent": not rotation_spikes,
        },
    }
    report["qa"]["passed"] = all((
        report["qa"]["finite_transforms"], report["qa"]["root_stable_for_in_place"], report["qa"]["rotation_spikes_absent"],
    ))
    write_json(report_path, report)
    print("V3_RETARGET_COMPLETE", json.dumps({"motion_id": args.motion_id, "frames": output_count, "qa": report["qa"], "report": str(report_path)}))
    return 0 if report["qa"]["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
