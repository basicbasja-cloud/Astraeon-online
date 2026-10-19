"""Create the action-free V3 copy of the V2 mannequin source scene."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--rig-spec-sha256", required=True)
    parser.add_argument("--strip-script-sha256", required=True)
    parser.add_argument("--expected-armature", required=True)
    parser.add_argument("--expected-bones", required=True)
    args = parser.parse_args(argv)

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    manifest_path = Path(args.manifest).resolve()
    actual_source_hash = sha256(source)
    if actual_source_hash != args.expected_source_sha256:
        raise RuntimeError(
            f"Source scene hash changed: expected {args.expected_source_sha256}, got {actual_source_hash}"
        )

    bpy.ops.wm.open_mainfile(filepath=str(source))
    rig = bpy.data.objects.get(args.expected_armature)
    if rig is None or rig.type != "ARMATURE":
        raise RuntimeError(f"Expected armature is missing: {args.expected_armature}")
    expected_bones = json.loads(args.expected_bones)
    actual_bones = [bone.name for bone in rig.data.bones]
    if actual_bones != expected_bones:
        missing = sorted(set(expected_bones) - set(actual_bones))
        extra = sorted(set(actual_bones) - set(expected_bones))
        raise RuntimeError(f"Rig bone contract changed (missing={missing}, extra={extra})")

    removed_actions = sorted(action.name for action in bpy.data.actions)
    # Remove every action binding first, including bindings on data blocks that
    # are not objects. This prevents a saved NLA/action strip from reappearing.
    for collection_name in ("objects", "scenes", "shape_keys", "materials", "worlds", "cameras", "lights"):
        collection = getattr(bpy.data, collection_name, ())
        for datablock in collection:
            if getattr(datablock, "animation_data", None) is not None:
                datablock.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action, do_unlink=True)
    if len(bpy.data.actions):
        raise RuntimeError(f"V2 actions remain after stripping: {[a.name for a in bpy.data.actions]}")

    for scene in bpy.data.scenes:
        if "clips" in scene:
            del scene["clips"]
        scene.frame_set(scene.frame_start)
    for pose_bone in rig.pose.bones:
        pose_bone.location = (0.0, 0.0, 0.0)
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pose_bone.scale = (1.0, 1.0, 1.0)

    scene = bpy.context.scene
    root = bpy.data.objects.get("ROOT_FantasyCharacter01")
    if root is None:
        raise RuntimeError("V2 root control ROOT_FantasyCharacter01 is missing")
    root.rotation_euler.z = 0.0
    scene["factoryV3RigId"] = "astraeon_humanoid_male_v1"
    scene["factoryV3SourceSceneSha256"] = actual_source_hash
    scene["factoryV3LegacyActionsRemoved"] = json.dumps(removed_actions)
    scene["factoryV3ActionPolicy"] = "V2 actions deleted; V3 production motions require external sources and provenance."

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    record = {
        "schema_version": 1,
        "rig_id": "astraeon_humanoid_male_v1",
        "source_scene": str(source),
        "source_scene_sha256": actual_source_hash,
        "rig_spec_sha256": args.rig_spec_sha256,
        "strip_script_sha256": args.strip_script_sha256,
        "output_scene": str(output),
        "output_scene_sha256": sha256(output),
        "armature": rig.name,
        "bone_count": len(actual_bones),
        "bones": actual_bones,
        "removed_action_count": len(removed_actions),
        "removed_actions": removed_actions,
        "remaining_action_count": len(bpy.data.actions),
        "camera": scene.camera.name if scene.camera else None,
        "camera_type": scene.camera.data.type if scene.camera else None,
        "camera_ortho_scale": scene.camera.data.ortho_scale if scene.camera and scene.camera.data.type == "ORTHO" else None,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "status": "ACTION_FREE_RIG_SMOKE_ONLY",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FACTORY_V3_RIG_CREATED", json.dumps({k: record[k] for k in ("bone_count", "removed_action_count", "remaining_action_count", "output_scene_sha256")}))


if __name__ == "__main__":
    main()
