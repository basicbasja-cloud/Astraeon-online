#!/usr/bin/env python3
"""Reusable offline engine for true modular, painted 2D character assets.

Class-specific style modules author their own SVG for each part from one shared
pose object. This engine owns registration, deterministic frame layout, raster
baking, composition, and structural validation. No whole-character extraction
or runtime skeletal rendering is performed.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from PIL import Image

CANONICAL_DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]


def validate_blueprint(spec: dict) -> None:
    errors = []

    def check(ok, message):
        if not ok:
            errors.append(message)

    check(spec.get("schemaVersion") == "1.0", "schemaVersion must be 1.0")
    check(bool(spec.get("characterId")), "characterId is required")
    check(bool(spec.get("classId")), "classId is required")
    check(spec.get("bodyVariant") in ("male", "female"), "bodyVariant must be male or female")
    check(spec.get("directions") == CANONICAL_DIRECTIONS, "direction order must be S,SW,W,NW,N,NE,E,SE")
    registration = spec.get("registration", {})
    canvas = registration.get("canvas")
    root = registration.get("root")
    check(isinstance(canvas, list) and len(canvas) == 2 and all(isinstance(v, int) and v > 0 for v in canvas),
          "registration.canvas must be two positive integers")
    check(isinstance(root, list) and len(root) == 2 and all(isinstance(v, (int, float)) for v in root),
          "registration.root must be an x,y pair")
    if isinstance(canvas, list) and isinstance(root, list) and len(canvas) == 2 and len(root) == 2:
        check(0 <= root[0] <= canvas[0] and 0 <= root[1] <= canvas[1], "root must be inside the frame canvas")
    check(registration.get("mirroring") == "none", "direction mirroring must be disabled")
    layers = spec.get("authoringLayers", [])
    layer_ids = [layer.get("id") for layer in layers if isinstance(layer, dict)]
    check(len(layers) >= 5 and len(layer_ids) == len(layers) and len(set(layer_ids)) == len(layer_ids),
          "authoringLayers must contain unique, named editable parts")
    runtime_slots = {layer.get("runtimeSlot") for layer in layers if isinstance(layer, dict)}
    check(all(bool(slot) for slot in runtime_slots), "every authoring part needs a runtimeSlot")
    runtime_compile = spec.get("runtimeCompile", {})
    check(bool(runtime_compile), "runtimeCompile mapping is required")
    check(runtime_slots.issubset(set(runtime_compile)), "every runtimeSlot needs a compile entry")
    compiled_parts = [part for parts in runtime_compile.values() for part in parts]
    check(sorted(compiled_parts) == sorted(layer_ids), "runtimeCompile must include every authoring part exactly once")
    sockets = spec.get("sockets", [])
    check("root" in sockets and len(sockets) == len(set(sockets)), "sockets must be unique and include root")
    clips = spec.get("clips", {})
    check(isinstance(clips, dict) and bool(clips), "at least one clip definition is required")
    for clip_id, clip in clips.items():
        count = clip.get("frames")
        check(isinstance(count, int) and count > 0, f"{clip_id}: frames must be positive")
        timing = clip.get("durationsMs")
        check(isinstance(timing, list) and len(timing) == count and all(isinstance(v, int) and v > 0 for v in timing),
              f"{clip_id}: durationsMs must contain one positive duration per frame")
        check(isinstance(clip.get("loop"), bool), f"{clip_id}: loop policy is required")
    for clip_id in spec.get("releaseRequiredClips", []):
        check(clip_id in clips, f"releaseRequiredClips references undefined {clip_id}")
    for clip_id in spec.get("optionalSupportedClips", []):
        check(clip_id in clips, f"optionalSupportedClips references undefined {clip_id}")
    if errors:
        raise ValueError("Invalid character blueprint:\n- " + "\n- ".join(errors))


class ModularCharacterEngine:
    """Bake independent authoring parts from a pluggable painted style module.

    Renderer protocol:
      - pose_for(direction, clip_id, frame_index) -> pose dict
      - svg_strip_for(layer_id, poses, palette, appearance) -> full-canvas SVG strip
      - composite(layer_images_by_id, direction) -> full-canvas RGBA image
      - make_sheet(named_images, destination, cols=..., scale=...)
    """

    def __init__(self, spec: dict, renderer, output: Path, inkscape: str = "inkscape"):
        validate_blueprint(spec)
        self.spec = spec
        self.renderer = renderer
        self.output = Path(output)
        self.inkscape = inkscape
        self.width, self.height = spec["registration"]["canvas"]
        self.root = spec["registration"]["root"]
        self.layer_ids = [layer["id"] for layer in spec["authoringLayers"]]

    def _render_strip(self, layer_id: str, clip_id: str, direction: str, poses: list[dict], palette: dict,
                      appearance: dict) -> Image.Image:
        folder = self.output / "authoring-source" / layer_id / clip_id
        folder.mkdir(parents=True, exist_ok=True)
        svg = self.renderer.svg_strip_for(layer_id, poses, palette, appearance)
        source = folder / f"{direction}.svg"
        source.write_text(svg, encoding="utf-8")
        png = self.output / "raster" / layer_id / clip_id / f"{direction}.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [self.inkscape, str(source), "--export-area-page",
             f"--export-width={self.width * len(poses)}", f"--export-height={self.height}",
             f"--export-filename={png}"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        image = Image.open(png).convert("RGBA")
        if image.size != (self.width * len(poses), self.height):
            raise ValueError(f"{layer_id}/{clip_id}/{direction}: bad strip size {image.size}")
        return image

    def bake(self, clips: list[str] | None = None) -> dict:
        requested = clips or list(self.spec["clips"])
        undefined = [clip for clip in requested if clip not in self.spec["clips"]]
        if undefined:
            raise ValueError("Undefined clips: " + ", ".join(undefined))
        palette = self.spec["palette"]
        appearance = self.spec.get("defaultAppearance", {})
        all_poses = {}
        review_sheets = {}
        clip_summary = {}
        for clip_id in requested:
            clip = self.spec["clips"][clip_id]
            count = clip["frames"]
            clip_summary[clip_id] = {"framesPerDirection": count, "loop": clip["loop"]}
            review_frames = []
            all_direction_strips = {layer: {} for layer in self.layer_ids}
            for direction in CANONICAL_DIRECTIONS:
                poses = [self.renderer.pose_for(direction, clip_id, frame) for frame in range(count)]
                for index, pose in enumerate(poses):
                    expected = {"clip": clip_id, "direction": direction, "frame": index, "root": self.root}
                    for key, value in expected.items():
                        if pose.get(key) != value:
                            raise ValueError(f"Pose registration mismatch {clip_id}/{direction}/{index}: {key}")
                    if "sockets" not in pose or "bones" not in pose:
                        raise ValueError(f"Pose is missing sockets/bones: {clip_id}/{direction}/{index}")
                    all_poses[f"{clip_id}/{direction}/{index:02}"] = pose
                strips = {layer: self._render_strip(layer, clip_id, direction, poses, palette, appearance)
                          for layer in self.layer_ids}
                for layer in self.layer_ids:
                    all_direction_strips[layer][direction] = strips[layer]
                for frame in range(count):
                    images = {layer: strips[layer].crop((frame*self.width, 0, (frame+1)*self.width, self.height))
                              for layer in self.layer_ids}
                    composite = self.renderer.composite(images, direction)
                    if composite.size != (self.width, self.height):
                        raise ValueError(f"Composite canvas mismatch at {clip_id}/{direction}/{frame}")
                    target = self.output / "composite-frames" / clip_id / direction / f"{frame:02}.png"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    composite.save(target)
                    if clip_id == "Idle" and frame == 0:
                        review_frames.append((direction, composite))
            if clip_id == "Idle":
                review_sheets["idle-eight-directions.png"] = review_frames
                target = self.output / "review" / "idle-eight-directions.png"
                self.renderer.make_sheet(review_frames, target, cols=4, scale=2)
            for layer in self.layer_ids:
                atlas = Image.new("RGBA", (self.width * count, self.height * len(CANONICAL_DIRECTIONS)), (0, 0, 0, 0))
                for row, direction in enumerate(CANONICAL_DIRECTIONS):
                    atlas.alpha_composite(all_direction_strips[layer][direction], (0, row * self.height))
                target = self.output / "authoring-atlases" / layer / f"{clip_id}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                atlas.save(target)
        poses_path = self.output / "pose-rig" / "poses.json"
        poses_path.parent.mkdir(parents=True, exist_ok=True)
        poses_path.write_text(json.dumps({
            "directions": CANONICAL_DIRECTIONS,
            "poseConvention": self.spec["registration"],
            "poses": all_poses,
            "status": self.spec["approvalStatus"],
        }, indent=2) + "\n", encoding="utf-8")
        manifest = {
            "schemaVersion": self.spec["schemaVersion"],
            "characterId": self.spec["characterId"],
            "classId": self.spec["classId"],
            "bodyVariant": self.spec["bodyVariant"],
            "approvalStatus": self.spec["approvalStatus"],
            "directions": CANONICAL_DIRECTIONS,
            "clipsBuilt": clip_summary,
            "releaseRequiredClips": self.spec.get("releaseRequiredClips", []),
            "optionalSupportedClips": self.spec.get("optionalSupportedClips", []),
            "authoringLayers": self.spec["authoringLayers"],
            "runtimeCompile": self.spec["runtimeCompile"],
            "registration": self.spec["registration"],
            "sockets": self.spec["sockets"],
            "drawOrderByDirection": {direction: self.renderer.order_for(direction) for direction in CANONICAL_DIRECTIONS},
            "frameRegistration": "full canvas, shared pose source, root and socket map; no trim or direction mirroring",
            "bakedAtlasFormat": "320px authoring frames; one layer/clip PNG; direction rows in canonical order; frame columns; requires reviewed runtime compilation",
        }
        (self.output / "authoring-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        atlas_meta = {
            "schemaVersion": "1.0",
            "characterId": self.spec["characterId"],
            "classId": self.spec["classId"],
            "bodyVariant": self.spec["bodyVariant"],
            "status": self.spec["approvalStatus"],
            "directions": CANONICAL_DIRECTIONS,
            "frame": {"width": self.width, "height": self.height, "root": self.root},
            "atlases": [
                {"layer": layer, "clip": clip_id, "file": f"authoring-atlases/{layer}/{clip_id}.png",
                 "width": self.width * self.spec["clips"][clip_id]["frames"],
                 "height": self.height * len(CANONICAL_DIRECTIONS),
                 "rows": {direction: row for row, direction in enumerate(CANONICAL_DIRECTIONS)},
                 "columns": {str(frame): frame for frame in range(self.spec["clips"][clip_id]["frames"])},
                 "durationsMs": self.spec["clips"][clip_id]["durationsMs"]}
                for clip_id in requested for layer in self.layer_ids
            ]
        }
        (self.output / "authoring-atlases" / "atlas-metadata.json").write_text(json.dumps(atlas_meta, indent=2) + "\n", encoding="utf-8")
        (self.output / "blueprint.json").write_text(json.dumps(self.spec, indent=2) + "\n", encoding="utf-8")
        return {"poses": all_poses, "reviewSheets": review_sheets, "manifest": manifest}
