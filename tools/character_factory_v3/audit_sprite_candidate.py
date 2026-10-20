#!/usr/bin/env python3
"""Write a diagnostic continuity and readability report for a packed sprite package.

Silhouette IoU is a review signal borrowed from the V3 research continuity audit.
It is not a quality score: intentional attack poses can change the silhouette.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

DIRECTIONS = ("S", "SW", "W", "NW", "N", "NE", "E", "SE")
RESEARCH_IOU_WARNING = 0.88
ALPHA_THRESHOLD = 8


def _frame_id(character_id: str, part_id: str, action: str, direction: str, index: int) -> str:
    return f"{character_id}_{part_id}_{action}_{direction}_{index:02d}"


def _crop_atlas(
    definition: dict[str, Any],
    part_id: str,
    action: str,
    direction: str,
    index: int,
    root: Path,
    cache: dict[str, Image.Image],
) -> Image.Image:
    width = int(definition["canvas"]["frameWidth"])
    height = int(definition["canvas"]["frameHeight"])
    part = definition["parts"][part_id]
    frame = part.get("frames", {}).get(_frame_id(definition["characterId"], part_id, action, direction, index))
    if frame is None:
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))
    atlas_id = frame["atlasId"]
    atlas = definition["atlases"][atlas_id]
    image = cache.get(atlas_id)
    if image is None:
        with Image.open(root / atlas["file"]) as opened:
            image = opened.convert("RGBA")
        if image.size != (atlas["width"], atlas["height"]):
            raise ValueError(f"Atlas size mismatch: {atlas_id}")
        cache[atlas_id] = image
    x, y, w, h = frame["rect"]
    return image.crop((x, y, x + w, y + h))


def _sample_full_pose(
    definition: dict[str, Any], action: str, direction: str, index: int, root: Path,
    cache: dict[str, Image.Image],
) -> Image.Image:
    width = int(definition["canvas"]["frameWidth"])
    height = int(definition["canvas"]["frameHeight"])
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for slot in definition["drawOrder"]:
        part_id = definition["defaultParts"][slot]
        layer = _crop_atlas(definition, part_id, action, direction, index, root, cache)
        result.alpha_composite(layer)
    return result


def _mask_metrics(image: Image.Image) -> dict[str, Any]:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    mask = alpha > ALPHA_THRESHOLD
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return {"visible": False, "bbox": None, "height_px": 0, "bottom_y": None, "centroid": None}
    return {
        "visible": True,
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)],
        "height_px": int(ys.max() + 1 - ys.min()),
        "bottom_y": int(ys.max()),
        "centroid": [float(xs.mean()), float(ys.mean())],
        "alpha_pixels": int(mask.sum()),
    }


def _iou(left: Image.Image, right: Image.Image) -> float:
    a = np.asarray(left.getchannel("A"), dtype=np.uint8) > ALPHA_THRESHOLD
    b = np.asarray(right.getchannel("A"), dtype=np.uint8) > ALPHA_THRESHOLD
    union = int(np.logical_or(a, b).sum())
    return 1.0 if union == 0 else float(np.logical_and(a, b).sum() / union)


def audit_definition(definition_path: Path, actions: list[str] | None = None) -> dict[str, Any]:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    root = definition_path.resolve().parents[3]
    cache: dict[str, Image.Image] = {}
    selected_actions = actions or [name for name in ("Idle", "Walk", "BasicAttack") if name in definition["clips"]]
    results: dict[str, Any] = {}
    errors: list[str] = []
    for action in selected_actions:
        clip = definition.get("clips", {}).get(action)
        if clip is None:
            errors.append(f"Missing action: {action}")
            continue
        count = len(clip["durations"])
        for direction in DIRECTIONS:
            poses = [_sample_full_pose(definition, action, direction, index, root, cache) for index in range(count)]
            metrics = [_mask_metrics(image) for image in poses]
            if any(not item["visible"] for item in metrics):
                errors.append(f"Empty composed frame in {action}/{direction}")
            pairs = [(index, index + 1) for index in range(count - 1)]
            if clip.get("loop") and count > 1:
                pairs.append((count - 1, 0))
            continuities = [
                {"from": left, "to": right, "iou": round(_iou(poses[left], poses[right]), 4)}
                for left, right in pairs
            ]
            heights = [item["height_px"] for item in metrics if item["visible"]]
            bottoms = [item["bottom_y"] for item in metrics if item["visible"]]
            centroids = [item["centroid"] for item in metrics if item["visible"]]
            centroid_jumps = [
                float(np.linalg.norm(np.asarray(centroids[i + 1]) - np.asarray(centroids[i])))
                for i in range(len(centroids) - 1)
            ]
            values = [item["iou"] for item in continuities]
            results.setdefault(action, {})[direction] = {
                "frame_count": count,
                "height_px": {"min": min(heights, default=0), "max": max(heights, default=0)},
                "bottom_y_range_px": max(bottoms, default=0) - min(bottoms, default=0),
                "max_centroid_shift_px": round(max(centroid_jumps, default=0.0), 3),
                "silhouette_iou": {
                    "mean": round(float(np.mean(values)), 4) if values else 1.0,
                    "min": round(min(values), 4) if values else 1.0,
                    "below_0_88_pairs": [pair for pair in continuities if pair["iou"] < RESEARCH_IOU_WARNING],
                    "pairs": continuities,
                },
            }

    action_summary: dict[str, Any] = {}
    for action, directions in results.items():
        clip = definition["clips"][action]
        means = [value["silhouette_iou"]["mean"] for value in directions.values()]
        minima = [value["silhouette_iou"]["min"] for value in directions.values()]
        action_summary[action] = {
            "silhouette_iou_mean_across_directions": round(float(np.mean(means)), 4) if means else 1.0,
            "silhouette_iou_min_across_directions": round(min(minima), 4) if minima else 1.0,
            "directions_below_0_88_mean": [direction for direction, value in directions.items()
                                                   if value["silhouette_iou"]["mean"] < RESEARCH_IOU_WARNING],
            "duration_ms": clip.get("durations", []) if action in definition["clips"] else [],
            "duration_imbalance_max_min": round(max(clip["durations"]) / min(clip["durations"]), 3)
            if action in definition["clips"] and min(definition["clips"][action]["durations"]) > 0 else None,
            "events": clip.get("events", []) if action in definition["clips"] else [],
            "loop": bool(clip.get("loop")) if action in definition["clips"] else False,
        }

    slot_parts = {
        slot: part_id for slot, part_id in definition.get("defaultParts", {}).items()
    }
    weapon_part = slot_parts.get("Weapon")
    fx_part = slot_parts.get("FX") or slot_parts.get("CosmeticFX")
    weapon_visible = False
    fx_visible = False
    if "BasicAttack" in definition.get("clips", {}):
        for direction in DIRECTIONS:
            for index in range(len(definition["clips"]["BasicAttack"]["durations"])):
                if weapon_part in definition.get("parts", {}):
                    weapon_visible |= _mask_metrics(_crop_atlas(definition, weapon_part, "BasicAttack", direction, index, root, cache))["visible"]
                if fx_part in definition.get("parts", {}):
                    fx_visible |= _mask_metrics(_crop_atlas(definition, fx_part, "BasicAttack", direction, index, root, cache))["visible"]
    return {
        "schema_version": 1,
        "candidate": definition.get("characterId"),
        "candidate_status": definition.get("source", {}).get("status"),
        "audited_definition": str(definition_path),
        "review_status": "DIAGNOSTIC_ONLY_VISUAL_REVIEW_REQUIRED",
        "research_reference": {
            "branch": "research/modular-sprites-full-body-2026-10-11",
            "signal": "adjacent-frame alpha silhouette IoU",
            "warning_threshold": RESEARCH_IOU_WARNING,
            "interpretation": "A low score flags a frame pair for inspection; intentional pose changes can lower attack IoU, so this is not an art-quality verdict.",
        },
        "readability": {
            "independent_weapon_part": weapon_part,
            "weapon_pixels_visible": bool(weapon_visible),
            "separate_combat_fx_part": fx_part,
            "combat_fx_pixels_visible": bool(fx_visible),
            "default_back_accessory": slot_parts.get("Back"),
            "default_parts": slot_parts,
            "fused_composite_tags": [tag for tag in definition.get("tags", []) if "FUSED" in tag or "COMPOSITE" in tag],
        },
        "summary": action_summary,
        "directions": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("definition", type=Path)
    parser.add_argument("--actions", nargs="+", default=None)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_definition(args.definition.resolve(), args.actions)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
