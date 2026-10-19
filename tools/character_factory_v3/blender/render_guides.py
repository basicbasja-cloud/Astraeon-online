"""Render an explicitly non-production, eight-direction static rig smoke set."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio
from bpy_extras.object_utils import world_to_camera_view

DIRECTIONS = (("S", 0), ("SW", -45), ("W", -90), ("NW", -135), ("N", -180), ("NE", -225), ("E", -270), ("SE", 45))
GROUP_IDS = {"BodyOutfit": 1, "HeadHair": 2, "Cape": 3, "Weapon": 4, "Headgear": 5, "Offhand": 6}
SEGMENT_COLORS = {1: (235, 83, 69), 2: (248, 207, 74), 3: (74, 151, 238), 4: (240, 240, 240), 5: (177, 88, 212), 6: (71, 205, 161)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_image(path: Path) -> np.ndarray:
    image_input = oiio.ImageInput.open(str(path))
    if image_input is None:
        raise RuntimeError(f"OpenImageIO could not read {path}: {oiio.geterror()}")
    try:
        spec = image_input.spec()
        if (spec.width, spec.height) != (320, 320):
            raise RuntimeError(f"Unexpected render pass size for {path}: {spec.width}x{spec.height}")
        return np.asarray(image_input.read_image(format=oiio.FLOAT), dtype=np.float32)
    finally:
        image_input.close()


def write_png(path: Path, rgba: np.ndarray) -> None:
    pixels = np.asarray(np.clip(np.rint(rgba * 255.0), 0, 255), dtype=np.uint8)
    if pixels.shape != (320, 320, 4):
        raise RuntimeError(f"Expected 320x320 RGBA pixels for {path}, got {pixels.shape}")
    spec = oiio.ImageSpec(320, 320, 4, oiio.UINT8)
    spec.channelnames = ["R", "G", "B", "A"]
    output = oiio.ImageOutput.create(str(path))
    if output is None or not output.open(str(path), spec):
        raise RuntimeError(f"OpenImageIO could not create {path}: {oiio.geterror()}")
    try:
        if not output.write_image(pixels):
            raise RuntimeError(f"OpenImageIO could not write {path}: {oiio.geterror()}")
    finally:
        output.close()


def add_file_output(tree, source_node, name: str, socket_name: str, socket_type: str):
    node = tree.nodes.new("CompositorNodeOutputFile")
    node.file_name = f"{name}_"
    item = node.file_output_items.new(socket_type, name)
    tree.links.new(source_node.outputs[socket_name], node.inputs[item.name])
    return node


def render_production_guides(guide_input_path: Path, output_root: Path, expected_armature: str) -> None:
    guide_input = json.loads(guide_input_path.read_text(encoding="utf-8"))
    rig_spec = guide_input["rig_spec"]
    actions_input = guide_input["actions"]
    if not actions_input:
        raise RuntimeError("Production render needs at least one sampled action")
    output_root.mkdir(parents=True, exist_ok=True)
    frames = []
    action_records = {}
    segmentation_colors = {module: SEGMENT_COLORS[object_id] for module, object_id in GROUP_IDS.items()}

    for action_name, item in actions_input.items():
        scene_path = Path(item["scene"]).resolve()
        scene_hash = sha256(scene_path)
        bpy.ops.wm.open_mainfile(filepath=str(scene_path))
        if len(bpy.data.actions) != 1:
            raise RuntimeError(f"{action_name} scene must contain exactly one retargeted V3 action")
        rig = bpy.data.objects.get(expected_armature)
        root_control = bpy.data.objects.get("ROOT_FantasyCharacter01")
        scene = bpy.context.scene
        if rig is None or root_control is None or scene.camera is None:
            raise RuntimeError(f"{action_name} guide scene is missing its V3 rig, root, or camera")
        action = rig.animation_data.action if rig.animation_data else None
        if action is None or not action.name.startswith("V3_"):
            raise RuntimeError(f"{action_name} scene contains no isolated V3 action")
        if scene.camera.data.type != "ORTHO":
            raise RuntimeError("V3 camera must remain orthographic")

        width = height = 320
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.image_settings.color_depth = "8"
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = 16
        scene.cycles.use_denoising = True
        scene.render.use_compositing = True
        scene.view_settings.view_transform = "Standard"
        view_layer = scene.view_layers[0]
        view_layer.use_pass_z = True
        view_layer.use_pass_normal = True
        view_layer.use_pass_object_index = True
        for obj in scene.objects:
            module = obj.get("spriteModule")
            if module in GROUP_IDS:
                obj.pass_index = GROUP_IDS[module]

        tree = bpy.data.node_groups.new("Factory V3 Animated Structural Passes", "CompositorNodeTree")
        scene.compositing_node_group = tree
        tree.nodes.clear()
        render_layer = tree.nodes.new("CompositorNodeRLayers")
        raw_nodes = {
            "depth": add_file_output(tree, render_layer, "depth", "Depth", "RGBA"),
            "normal": add_file_output(tree, render_layer, "normal", "Normal", "RGBA"),
            "object_index": add_file_output(tree, render_layer, "object_index", "Object Index", "RGBA"),
        }
        masks = {}
        for module, object_id in GROUP_IDS.items():
            mask_node = tree.nodes.new("CompositorNodeIDMask")
            mask_node.inputs["Index"].default_value = object_id
            mask_node.inputs["Anti-Alias"].default_value = True
            tree.links.new(render_layer.outputs["Object Index"], mask_node.inputs["ID value"])
            masks[module] = add_file_output(tree, mask_node, f"mask_{module}", "Alpha", "FLOAT")

        timeline = item["timeline"]
        if timeline.get("frame_count") != len(timeline.get("frames", [])):
            raise RuntimeError(f"{action_name} sampled timeline frame count is inconsistent")
        action_records[action_name] = {
            "motion_id": timeline["motion_id"],
            "source_action": timeline.get("source_action"),
            "source_fps": timeline["source_fps"],
            "output_fps": timeline["output_fps"],
            "source_frame_range": timeline["source_frame_range"],
            "retarget_frame_range": timeline["retarget_frame_range"],
            "loop": timeline["loop"],
            "frame_count": timeline["frame_count"],
            "durations": [frame["duration_ms"] for frame in timeline["frames"]],
            "duration_ms": timeline["duration_ms"],
            "semantic_phases": timeline.get("semantic_phases", {}),
            "events": timeline.get("events", []),
            "motion_provenance": item["motion_provenance"],
            "retarget_report": item["retarget_report"],
            "retarget_report_sha256": sha256(Path(item["retarget_report_path"]).resolve()),
            "retarget_scene_sha256": scene_hash,
            "qa": item.get("qa", {}),
            "source_root_motion": item.get("source_root_motion", {}),
            "foot_contacts": item.get("foot_contacts", {}),
        }
        anchors = {
            "root": "root",
            "head": rig_spec["anchor_bones"]["head"],
            "hand_R": rig_spec["anchor_bones"]["weapon_right_hand"],
            "hand_L": rig_spec["anchor_bones"]["offhand_or_shield"],
            "back": rig_spec["anchor_bones"]["back_accessory"],
            "waist": "Hips",
        }
        with tempfile.TemporaryDirectory(prefix=f"astraeon-v3-{action_name.lower()}-") as temp:
            raw_root = Path(temp)
            for timeline_frame in timeline["frames"]:
                frame_index = timeline_frame["frame_index"]
                retarget_frame = int(timeline_frame["retarget_frame"])
                for direction, yaw in DIRECTIONS:
                    root_control.rotation_euler.z = math.radians(yaw)
                    scene.frame_set(retarget_frame)
                    bpy.context.view_layer.update()
                    frame_root = output_root / "actions" / action_name / f"frame-{frame_index:02d}" / direction
                    frame_root.mkdir(parents=True, exist_ok=True)
                    raw_dir = raw_root / f"{frame_index:02d}_{direction}"
                    raw_dir.mkdir(parents=True, exist_ok=True)
                    for node in [*raw_nodes.values(), *masks.values()]:
                        node.directory = str(raw_dir)
                    rgb_path = frame_root / "rgb.png"
                    scene.render.filepath = str(rgb_path.with_suffix(""))
                    result = bpy.ops.render.render(write_still=True)
                    if "FINISHED" not in result or not rgb_path.is_file():
                        raise RuntimeError(f"RGB render failed at {action_name}/{frame_index}/{direction}")
                    rgb = read_image(rgb_path)
                    raw_passes = {}
                    for name in raw_nodes:
                        path = raw_dir / f"{name}_.exr"
                        if not path.is_file():
                            raise RuntimeError(f"Missing {name} compositor pass for {action_name}/{frame_index}/{direction}")
                        raw_passes[name] = read_image(path)
                    for module in GROUP_IDS:
                        path = raw_dir / f"mask_{module}_.exr"
                        if not path.is_file():
                            raise RuntimeError(f"Missing {module} segmentation mask for {action_name}/{frame_index}/{direction}")
                        raw_passes[f"mask_{module}"] = read_image(path)

                    alpha = np.clip(rgb[:, :, 3], 0.0, 1.0)
                    records = {"rgb": {"file": str(rgb_path.relative_to(output_root)), "sha256": sha256(rgb_path)}}

                    def emit(name: str, rgba: np.ndarray) -> None:
                        path = frame_root / f"{name}.png"
                        write_png(path, rgba)
                        records[name] = {"file": str(path.relative_to(output_root)), "sha256": sha256(path)}

                    silhouette = np.ones((height, width, 4), dtype=np.float32)
                    silhouette[:, :, 3] = alpha
                    emit("silhouette", silhouette)

                    depth = raw_passes["depth"][:, :, 0]
                    valid = (alpha > 0.01) & np.isfinite(depth) & (depth < 1.0e9)
                    if np.any(valid):
                        near, far = float(depth[valid].min()), float(depth[valid].max())
                    else:
                        near, far = 0.0, 1.0
                    if far - near < 1.0e-8:
                        far = near + 1.0
                    normalized_depth = np.clip((depth - near) / (far - near), 0.0, 1.0)
                    normalized_depth[alpha <= 0.01] = 0.0
                    depth_rgba = np.repeat(normalized_depth[:, :, None], 4, axis=2)
                    depth_rgba[:, :, 3] = alpha
                    emit("depth", depth_rgba)

                    normal = raw_passes["normal"][:, :, :3]
                    normal_rgba = np.zeros((height, width, 4), dtype=np.float32)
                    normal_rgba[:, :, :3] = np.clip(normal * 0.5 + 0.5, 0.0, 1.0)
                    normal_rgba[:, :, 3] = alpha
                    emit("normal", normal_rgba)

                    object_ids = np.rint(raw_passes["object_index"][:, :, 0]).astype(np.int32)
                    segmentation = np.zeros((height, width, 4), dtype=np.float32)
                    for module, object_id in GROUP_IDS.items():
                        mask = np.clip(raw_passes[f"mask_{module}"][:, :, 0], 0.0, 1.0)
                        color = np.asarray(SEGMENT_COLORS[object_id], dtype=np.float32) / 255.0
                        selection = (object_ids == object_id) & (alpha > 0.01)
                        segmentation[selection, :3] = color
                        segmentation[selection, 3] = alpha[selection]
                        edge = selection & (mask > 0.0) & (mask < 1.0)
                        segmentation[edge, 3] = np.minimum(alpha[edge], mask[edge])
                    emit("body_segmentation", segmentation)

                    weapon = np.clip(raw_passes["mask_Weapon"][:, :, 0], 0.0, 1.0)
                    weapon_rgba = np.ones((height, width, 4), dtype=np.float32)
                    weapon_rgba[:, :, 3] = np.minimum(weapon, alpha)
                    emit("weapon_mask", weapon_rgba)

                    sockets = {"root": [160.0, 264.0]}
                    for socket, bone_name in anchors.items():
                        if socket == "root":
                            continue
                        pose_bone = rig.pose.bones.get(bone_name)
                        if pose_bone is None:
                            raise RuntimeError(f"Missing socket bone {bone_name} for {action_name}")
                        world = rig.matrix_world @ pose_bone.head
                        projected = world_to_camera_view(scene, scene.camera, world)
                        sockets[socket] = [round(projected.x * width, 4), round((1.0 - projected.y) * height, 4)]
                    frames.append({
                        "action": action_name,
                        "frame_index": frame_index,
                        "source_frame": timeline_frame["source_frame"],
                        "retarget_frame": retarget_frame,
                        "phase": timeline_frame["phase"],
                        "duration_ms": timeline_frame["duration_ms"],
                        "direction": direction,
                        "yaw_degrees": yaw,
                        "sockets": sockets,
                        "visible_alpha_pixels": int(np.count_nonzero(alpha > 0.01)),
                        "object_index_values": sorted(int(value) for value in np.unique(object_ids) if value != 0),
                        "depth_range": {"near": near, "far": far, "encoding": "per-frame linear normalized"},
                        "passes": records,
                    })

    manifest = {
        "schema_version": 1,
        "character_id": "swordsman_male_v3",
        "pose_kind": "PRODUCTION_ANIMATION",
        "status": "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING",
        "width": 320,
        "height": 320,
        "root_pixel": [160, 264],
        "directions": [name for name, _ in DIRECTIONS],
        "mirroring": "none",
        "camera": "CAM_FantasySprite",
        "camera_type": "ORTHO",
        "blender_version": bpy.app.version_string,
        "render_engine": "CYCLES_CPU",
        "segmentation": {"object_ids": GROUP_IDS, "colors_rgb": segmentation_colors},
        "logical_layer_limits": {
            "BaseBody": "Source BodyOutfit geometry combines body and outfit; this guide does not invent a split.",
            "Hair": "Source HeadHair geometry combines head and hair.",
            "Outfit": "No independent outfit mesh exists in the source scene.",
            "Weapon": "Sword mesh is attached to Hand.R.",
            "Headgear": "No headgear mesh exists in the source scene.",
            "BackAccessory": "Source Cape mesh is independently segmented.",
        },
        "actions": action_records,
        "frames": frames,
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FACTORY_V3_ANIMATION_GUIDES_RENDERED", json.dumps({"actions": len(action_records), "frames": len(frames), "output": str(output_root)}))


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene")
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-armature", default="ARM_FantasyCharacter01")
    parser.add_argument("--timelines", help="Sampled action scenes/timelines for production guide rendering")
    args = parser.parse_args(argv)
    output_root = Path(args.output).resolve()
    if args.timelines:
        render_production_guides(Path(args.timelines).resolve(), output_root, args.expected_armature)
        return
    if not args.scene:
        parser.error("--scene is required for static rig review")
    scene_path = Path(args.scene).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(scene_path))
    if len(bpy.data.actions) != 0:
        raise RuntimeError(f"Rig review scene contains {len(bpy.data.actions)} actions; V2 curves are forbidden")
    rig = bpy.data.objects.get(args.expected_armature)
    root = bpy.data.objects.get("ROOT_FantasyCharacter01")
    scene = bpy.context.scene
    if rig is None or root is None or scene.camera is None:
        raise RuntimeError("V3 rig, root, or camera is missing")
    if scene.camera.data.type != "ORTHO":
        raise RuntimeError("V3 camera must remain orthographic")

    width = height = 320
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    # EEVEE requires EGL/OpenGL on some headless agents. CPU Cycles is usable
    # from a clean background process and does not require a display or GPU.
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.use_compositing = True
    scene.view_settings.view_transform = "Standard"
    view_layer = scene.view_layers[0]
    view_layer.use_pass_z = True
    view_layer.use_pass_normal = True
    view_layer.use_pass_object_index = True
    for obj in scene.objects:
        module = obj.get("spriteModule")
        if module in GROUP_IDS:
            obj.pass_index = GROUP_IDS[module]

    # Blender 5.2 writes compositor File Output nodes as multilayer EXR. The
    # bundled OpenImageIO library reads the float data and writes portable PNGs.
    tree = bpy.data.node_groups.new("Factory V3 Structural Passes", "CompositorNodeTree")
    scene.compositing_node_group = tree
    tree.nodes.clear()
    render_layer = tree.nodes.new("CompositorNodeRLayers")
    raw_nodes = {
        "depth": add_file_output(tree, render_layer, "depth", "Depth", "RGBA"),
        "normal": add_file_output(tree, render_layer, "normal", "Normal", "RGBA"),
        "object_index": add_file_output(tree, render_layer, "object_index", "Object Index", "RGBA"),
    }
    masks = {}
    for module, object_id in GROUP_IDS.items():
        mask_node = tree.nodes.new("CompositorNodeIDMask")
        mask_node.inputs["Index"].default_value = object_id
        mask_node.inputs["Anti-Alias"].default_value = True
        tree.links.new(render_layer.outputs["Object Index"], mask_node.inputs["ID value"])
        masks[module] = add_file_output(tree, mask_node, f"mask_{module}", "Alpha", "FLOAT")

    output_root.mkdir(parents=True, exist_ok=True)
    raw_frames = []
    with tempfile.TemporaryDirectory(prefix="astraeon-factory-v3-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for direction, yaw in DIRECTIONS:
            root.rotation_euler.z = math.radians(yaw)
            scene.frame_set(scene.frame_start)
            bpy.context.view_layer.update()
            output_dir = output_root / direction
            output_dir.mkdir(parents=True, exist_ok=True)
            raw_dir = temporary_root / direction
            raw_dir.mkdir(parents=True, exist_ok=True)
            for node in [*raw_nodes.values(), *masks.values()]:
                node.directory = str(raw_dir)
            rgb_path = output_dir / "rgb.png"
            scene.render.filepath = str(rgb_path.with_suffix(""))
            result = bpy.ops.render.render(write_still=True)
            if "FINISHED" not in result or not rgb_path.is_file():
                raise RuntimeError(f"RGB render failed for {direction}: result={result}, expected={rgb_path}")
            raw = {}
            for name in raw_nodes:
                path = raw_dir / f"{name}_.exr"
                if not path.is_file():
                    raise RuntimeError(f"Missing compositor pass for {direction}: {path}")
                raw[name] = read_image(path)
            for module in GROUP_IDS:
                name = f"mask_{module}"
                path = raw_dir / f"{name}_.exr"
                if not path.is_file():
                    raise RuntimeError(f"Missing segmentation mask for {direction}: {path}")
                raw[name] = read_image(path)
            raw_frames.append({"direction": direction, "yaw": yaw, "rgb": read_image(rgb_path), "passes": raw, "root": output_dir})

    depth_values = []
    for frame in raw_frames:
        alpha = frame["rgb"][:, :, 3] > 0.01
        depth = frame["passes"]["depth"][:, :, 0]
        valid = alpha & np.isfinite(depth) & (depth < 1.0e9)
        depth_values.append(depth[valid])
    all_depth = np.concatenate([values for values in depth_values if values.size]) if any(v.size for v in depth_values) else np.array([0.0, 1.0], dtype=np.float32)
    depth_near = float(all_depth.min())
    depth_far = float(all_depth.max())
    if depth_far - depth_near < 1e-8:
        depth_far = depth_near + 1.0

    frames = []
    for frame in raw_frames:
        direction = frame["direction"]
        output_dir = frame["root"]
        rgb = frame["rgb"]
        alpha = np.clip(rgb[:, :, 3], 0.0, 1.0)
        records = {}

        def emit(name: str, rgba: np.ndarray) -> None:
            path = output_dir / f"{name}.png"
            write_png(path, rgba)
            records[name] = {"file": f"{direction}/{path.name}", "sha256": sha256(path)}

        emit("rgb", rgb)
        silhouette = np.zeros((height, width, 4), dtype=np.float32)
        silhouette[:, :, :3] = 1.0
        silhouette[:, :, 3] = alpha
        emit("silhouette", silhouette)

        depth = frame["passes"]["depth"][:, :, 0]
        normalized_depth = np.clip((depth - depth_near) / (depth_far - depth_near), 0.0, 1.0)
        normalized_depth[alpha <= 0.01] = 0.0
        depth_rgba = np.repeat(normalized_depth[:, :, None], 4, axis=2)
        depth_rgba[:, :, 3] = alpha
        emit("depth", depth_rgba)

        normal = frame["passes"]["normal"][:, :, :3]
        normal_rgba = np.zeros((height, width, 4), dtype=np.float32)
        normal_rgba[:, :, :3] = np.clip(normal * 0.5 + 0.5, 0.0, 1.0)
        normal_rgba[:, :, 3] = alpha
        emit("normal", normal_rgba)

        object_ids = np.rint(frame["passes"]["object_index"][:, :, 0]).astype(np.int32)
        segmentation = np.zeros((height, width, 4), dtype=np.float32)
        for module, object_id in GROUP_IDS.items():
            mask = np.clip(frame["passes"][f"mask_{module}"][:, :, 0], 0.0, 1.0)
            color = np.asarray(SEGMENT_COLORS[object_id], dtype=np.float32) / 255.0
            selection = (object_ids == object_id) & (alpha > 0.01)
            segmentation[selection, :3] = color
            segmentation[selection, 3] = alpha[selection]
            edge = selection & (mask > 0.0) & (mask < 1.0)
            segmentation[edge, 3] = np.minimum(alpha[edge], mask[edge])
        emit("body_segmentation", segmentation)

        weapon = np.clip(frame["passes"]["mask_Weapon"][:, :, 0], 0.0, 1.0)
        weapon_rgba = np.ones((height, width, 4), dtype=np.float32)
        weapon_rgba[:, :, 3] = np.minimum(weapon, alpha)
        emit("weapon_mask", weapon_rgba)
        frames.append({
            "direction": direction,
            "frame_index": 0,
            "yaw_degrees": frame["yaw"],
            "root_rotation_z": math.radians(frame["yaw"]),
            "visible_alpha_pixels": int(np.count_nonzero(alpha > 0.01)),
            "object_index_values": sorted(int(v) for v in np.unique(object_ids) if v != 0),
            "passes": records,
        })

    manifest = {
        "schema_version": 1,
        "character_id": "swordsman_male_v3",
        "pose_kind": "REST_ONLY_NONPRODUCTION",
        "status": "RIG_CAMERA_SMOKE_ONLY",
        "source_scene": str(scene_path),
        "source_scene_sha256": sha256(scene_path),
        "blender_version": bpy.app.version_string,
        "render_engine": "CYCLES_CPU",
        "width": width,
        "height": height,
        "root_pixel": [160, 264],
        "directions": [name for name, _ in DIRECTIONS],
        "mirroring": "none",
        "camera": scene.camera.name,
        "camera_type": scene.camera.data.type,
        "camera_ortho_scale": scene.camera.data.ortho_scale,
        "depth_range": {"near": depth_near, "far": depth_far, "encoding": "global linear normalized across this 8-direction static review set"},
        "segmentation": {"object_ids": GROUP_IDS, "colors_rgb": SEGMENT_COLORS},
        "source_group_semantics": "V2 groups are retained; BodyOutfit and HeadHair are combined source meshes, not separated painted layers.",
        "frames": frames,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FACTORY_V3_STATIC_GUIDES_RENDERED", json.dumps({"directions": len(frames), "passes": 6, "output": str(output_root)}))


if __name__ == "__main__":
    main()
