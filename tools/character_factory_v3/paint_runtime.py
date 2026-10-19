#!/usr/bin/env python3
"""Create a deterministic palette-locked paint candidate and runtime strips from V3 guides."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

from contracts import read_json, sha256_file, write_json
from qa import DIRECTIONS, validate_production_guide_manifest


SOURCE_MODULES = {
    "base-body": ("Body", "BodyOutfit"),
    "hair": ("Hair", "HeadHair"),
    "outfit": ("Outfit", None),
    "weapon": ("Weapon", "Weapon"),
    "headgear": ("Headgear", None),
    "back-accessory": ("Back", "Cape"),
}
GUIDE_SIZE = 320
RUNTIME_SIZE = 160
RUNTIME_SCALE = RUNTIME_SIZE / GUIDE_SIZE


def read_rgba(root: Path, frame: dict[str, Any], pass_name: str) -> Image.Image:
    relative = Path(frame["passes"][pass_name]["file"])
    path = root / relative
    with Image.open(path) as source:
        image = source.convert("RGBA")
        if image.size != (320, 320):
            raise ValueError(f"Expected 320x320 guide pass: {path}")
        return image.copy()


def make_locked_palette(manifest: dict[str, Any], root: Path) -> tuple[Image.Image, Image.Image]:
    frame_records = manifest.get("frames", [])
    samples = []
    for record in frame_records:
        source = read_rgba(root, record, "rgb")
        bounds = source.getchannel("A").getbbox()
        if bounds:
            samples.append(source.crop(bounds).convert("RGB").resize((80, 80), Image.Resampling.LANCZOS))
    if not samples:
        raise ValueError("No visible guide pixels are available for the shared palette")
    columns = 12
    rows = math.ceil(len(samples) / columns)
    palette_source = Image.new("RGB", (columns * 80, rows * 80), (74, 62, 53))
    for index, sample in enumerate(samples):
        palette_source.paste(sample, ((index % columns) * 80, (index // columns) * 80))
    reduced = palette_source.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette = Image.new("P", (1, 1))
    palette.putpalette(reduced.getpalette())
    return palette, palette_source


def stylize_frame(source: Image.Image, normal: Image.Image, palette: Image.Image) -> Image.Image:
    """Apply one global palette, restrained warmth, and soft warm internal linework."""
    rgba = source.convert("RGBA")
    alpha = rgba.getchannel("A")
    original = ImageEnhance.Color(rgba.convert("RGB")).enhance(0.92)
    quantized = original.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGB")
    painted = Image.blend(original, quantized, 0.38)
    painted = ImageEnhance.Brightness(painted).enhance(1.015)
    painted = ImageEnhance.Contrast(painted).enhance(0.97).filter(ImageFilter.SMOOTH)
    result = painted.convert("RGBA")
    result.putalpha(alpha)

    normal_rgb = np.asarray(normal.convert("RGB"), dtype=np.int16)
    differences = []
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        shifted = np.roll(normal_rgb, (dy, dx), axis=(0, 1))
        differences.append(np.max(np.abs(normal_rgb - shifted), axis=2))
    gradient = np.maximum.reduce(differences)
    edge_alpha = np.clip((gradient.astype(np.float32) - 32.0) * 0.16, 0.0, 18.0).astype(np.uint8)
    edge_alpha[np.asarray(alpha, dtype=np.uint8) == 0] = 0
    edge_image = Image.fromarray(edge_alpha, mode="L")
    edge_image = ImageChops.multiply(edge_image, alpha)
    outline = Image.new("RGBA", (320, 320), (86, 65, 50, 0))
    outline.putalpha(edge_image)
    return Image.alpha_composite(result, outline)


def module_alpha(segmentation: Image.Image, module: str | None, colors: dict[str, list[int]]) -> Image.Image:
    if module is None:
        return Image.new("L", (320, 320), 0)
    pixels = np.asarray(segmentation.convert("RGBA"), dtype=np.int16)
    color = np.asarray(colors[module], dtype=np.int16)
    match = (np.max(np.abs(pixels[:, :, :3] - color), axis=2) <= 3) & (pixels[:, :, 3] > 0)
    return Image.fromarray(np.where(match, pixels[:, :, 3], 0).astype(np.uint8), mode="L")


def clip_definition(action_record: dict[str, Any], tags: list[str]) -> dict[str, Any]:
    directions = {}
    frame_by_key: dict[tuple[int, str], dict[str, Any]] = {}
    for frame in action_record["rendered_frames"]:
        frame_by_key[(frame["frame_index"], frame["direction"])] = frame
    for direction in DIRECTIONS:
        directions[direction] = {
            "frames": [
                {
                    "frameIndex": index,
                    "sockets": {
                        socket: [round(value * RUNTIME_SCALE, 4) for value in point]
                        for socket, point in frame_by_key[(index, direction)]["sockets"].items()
                    },
                }
                for index in range(action_record["frame_count"])
            ]
        }
    return {
        "loop": action_record["loop"],
        "durations": action_record["durations"],
        "directions": directions,
        "tags": tags,
        "events": [
            {
                "name": event["name"],
                "phase": event["phase"],
                "timeMs": event["time_ms"],
                "frameIndex": event["frame_index"],
            }
            for event in action_record.get("events", [])
        ],
    }


def write_strips(manifest: dict[str, Any], guide_root: Path, output_root: Path) -> dict[str, Any]:
    colors = manifest["segmentation"]["colors_rgb"]
    guide_frames = manifest["frames"]
    actions: dict[str, dict[str, Any]] = {}
    for action_name, item in manifest["actions"].items():
        selected = sorted((frame for frame in guide_frames if frame["action"] == action_name), key=lambda frame: (frame["frame_index"], DIRECTIONS.index(frame["direction"])))
        if len(selected) != item["frame_count"] * len(DIRECTIONS):
            raise ValueError(f"Incomplete guide pixels for {action_name}")
        action_data = {**item, "rendered_frames": selected}
        actions[action_name] = action_data

    palette, palette_source = make_locked_palette(manifest, guide_root)
    palette_source.save(output_root / "palette-source.png", format="PNG", optimize=False)
    palette.save(output_root / "palette-index.png", format="PNG", optimize=False)
    painted_cache: dict[tuple[str, int, str], dict[str, Image.Image]] = {}
    for action_name, action_data in actions.items():
        count = action_data["frame_count"]
        strips = {
            part_id: Image.new("RGBA", (RUNTIME_SIZE * count, RUNTIME_SIZE * len(DIRECTIONS)), (0, 0, 0, 0))
            for part_id in SOURCE_MODULES
        }
        for frame in action_data["rendered_frames"]:
            key = (action_name, frame["frame_index"], frame["direction"])
            rgb = read_rgba(guide_root, frame, "rgb")
            normal = read_rgba(guide_root, frame, "normal")
            painted = stylize_frame(rgb, normal, palette)
            segmentation = read_rgba(guide_root, frame, "body_segmentation")
            row = DIRECTIONS.index(frame["direction"])
            col = frame["frame_index"]
            for part_id, (_, module) in SOURCE_MODULES.items():
                alpha = module_alpha(segmentation, module, colors)
                layer = painted.copy()
                layer.putalpha(alpha)
                layer = layer.resize((RUNTIME_SIZE, RUNTIME_SIZE), Image.Resampling.LANCZOS)
                strips[part_id].paste(layer, (col * RUNTIME_SIZE, row * RUNTIME_SIZE))
                painted_cache.setdefault(key, {})[part_id] = layer
        for part_id, strip in strips.items():
            target = output_root / "parts" / part_id / action_name / "strip.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            strip.save(target, format="PNG", optimize=False)

    idle_frames = actions["Idle"]["rendered_frames"]
    placeholders = {
        "Run": True,
        "SkillAction": False,
        "Hit": False,
        "Death": False,
        "Guard": True,
        "Dash": False,
    }
    for action_name, loop in placeholders.items():
        for part_id in SOURCE_MODULES:
            strip = Image.new("RGBA", (RUNTIME_SIZE, RUNTIME_SIZE * len(DIRECTIONS)), (0, 0, 0, 0))
            for direction_index, direction in enumerate(DIRECTIONS):
                source_frame = idle_frames[direction_index]
                layer = painted_cache[("Idle", source_frame["frame_index"], direction)][part_id]
                strip.paste(layer, (0, direction_index * RUNTIME_SIZE))
            target = output_root / "parts" / part_id / action_name / "strip.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            strip.save(target, format="PNG", optimize=False)

    real_tags = ["INTERNAL_VISUAL_PASS", "PROCEDURAL_PAINT_CANDIDATE", "OWNER_APPROVAL_PENDING"]
    clips = {
        action: clip_definition(item, real_tags)
        for action, item in actions.items()
    }
    for action, loop in placeholders.items():
        idle = clips["Idle"]
        directions = {}
        for direction in DIRECTIONS:
            directions[direction] = {"frames": [{"frameIndex": 0, "sockets": idle["directions"][direction]["frames"][0]["sockets"]}]}
        clips[action] = {
            "loop": loop,
            "durations": [800],
            "directions": directions,
            "tags": ["INTERNAL_PLACEHOLDER", "STATIC_IDLE_FALLBACK", "OWNER_APPROVAL_PENDING"],
            "events": [],
        }

    parts = {}
    for part_id, (slot, module) in SOURCE_MODULES.items():
        tags = []
        if module == "BodyOutfit":
            tags = ["SOURCE_BODY_AND_OUTFIT_COMBINED"]
        elif module == "HeadHair":
            tags = ["SOURCE_HEAD_AND_HAIR_COMBINED"]
        elif module == "Cape":
            tags = ["SOURCE_CAPE_MESH"]
        elif module == "Weapon":
            tags = ["SOURCE_SWORD_MESH"]
        else:
            tags = ["NO_INDEPENDENT_SOURCE_MESH"]
        parts[part_id] = {"slot": slot, "tags": tags, "frames": {}}

    definition = {
        "version": "0.1",
        "characterId": "swordsman-male-v3",
        "classId": "Swordsman",
        "bodyVariant": "male",
        "directions": list(DIRECTIONS),
        "mirroring": "none",
        "source": {
            "status": "DEV_ONLY",
            "reference": "authoring/characters/factory-v3/identities/swordsman_identity_v1.json",
            "approvedBy": None,
            "camera": "CAM_FantasySprite; orthographic; 320x320; root pixel 160,264",
            "handedness": "right",
            "normalization": {
                "sourceFrameWidth": GUIDE_SIZE,
                "sourceFrameHeight": GUIDE_SIZE,
                "sourceRootAnchor": [160, 264],
                "scale": 1.0,
            },
            "designLocks": [
                "approved male swordsman identity seed",
                "silver-lavender hair and mustard-gold cape",
                "right-hand narrow steel sword",
                "softly painted warm shading; no black outline",
                "owner review required before runtime admission",
            ],
        },
        "tags": ["DEV_ONLY", "PLACEHOLDER", "NOT_FINAL_ART", "INTERNAL_MOTION_REVIEW_CANDIDATE", "PROCEDURAL_PAINT_CANDIDATE"],
        "canvas": {"frameWidth": RUNTIME_SIZE, "frameHeight": RUNTIME_SIZE, "rootAnchorX": 80, "rootAnchorY": 132, "referenceHeight": 88},
        "slots": {"Body": "BaseBody", "Hair": "Hair", "Outfit": "Outfit", "Weapon": "Weapon", "Headgear": "Headgear", "Back": "BackAccessory"},
        "defaultParts": {"Body": "base-body", "Hair": "hair", "Outfit": "outfit", "Weapon": "weapon", "Headgear": "headgear", "Back": "back-accessory"},
        "drawOrder": ["Back", "Body", "Hair", "Outfit", "Weapon", "Headgear"],
        "clips": clips,
        "parts": parts,
        "atlases": {},
    }
    # Direction-key order is part of the runtime contract. Preserve the
    # canonical S, SW, W, NW, N, NE, E, SE insertion order in the JSON.
    (output_root / "sprite-definition.json").write_text(
        json.dumps(definition, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return {
        "palette_colors": 96,
        "palette_source_frames": len(manifest["frames"]),
        "actions": {name: item["frame_count"] for name, item in actions.items()},
        "placeholder_actions": sorted(placeholders),
        "layer_limits": manifest.get("logical_layer_limits", {}),
        "palette_lock": "One shared 96-color palette built from all 24 selected action poses in eight directions.",
        "stylization": "38% palette quantization blend, mild warm grade, low-contrast smoothing, warm normal-derived edges.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    guide_root = manifest_path.parent
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    gate = validate_production_guide_manifest(manifest_path, ["Idle", "Walk", "BasicAttack"])
    if not gate["passed"]:
        raise ValueError("Painter input failed guide QA:\n- " + "\n- ".join(gate["errors"]))
    manifest = read_json(manifest_path)
    paint_report = write_strips(manifest, guide_root, output_root)
    runtime_root = args.repository.resolve() / "assets" / "characters" / "swordsman-male-v3"
    runtime_root.mkdir(parents=True, exist_ok=True)
    provenance = {
        "schema_version": 1,
        "character_id": "swordsman_male_v3",
        "status": "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING",
        "source_manifest": str(manifest_path.relative_to(args.repository.resolve())),
        "source_manifest_sha256": sha256_file(manifest_path),
        "guide_status": manifest.get("status"),
        "owner_approved": False,
        "runtime_admitted": False,
        "actions": manifest.get("actions", {}),
        "paint_candidate": paint_report,
        "source_mesh_limitations": manifest.get("logical_layer_limits", {}),
        "legacy_v2_motion_fallback": False,
        "notes": [
            "The six runtime slots are emitted, but source meshes combine BodyOutfit and HeadHair.",
            "Outfit and Headgear are explicit empty candidates because the source scene has no independent meshes for those slots.",
            "This deterministic raster pass is a review candidate, not owner-approved final art.",
        ],
    }
    write_json(runtime_root / "motion-provenance.json", provenance)
    report_path = output_root / "paint-report.json"
    write_json(report_path, {"passed": True, **paint_report, "provenance_sidecar": str((runtime_root / "motion-provenance.json").relative_to(args.repository.resolve()))})
    print(json.dumps({"passed": True, "output": str(output_root), "report": str(report_path), "runtime_sidecar": str(runtime_root / "motion-provenance.json"), **paint_report}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"V3 procedural paint candidate stopped: {exc}", file=sys.stderr)
        raise SystemExit(1)
