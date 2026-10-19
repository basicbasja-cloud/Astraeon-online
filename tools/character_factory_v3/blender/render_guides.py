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


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-armature", required=True)
    args = parser.parse_args(argv)
    scene_path = Path(args.scene).resolve()
    output_root = Path(args.output).resolve()
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
