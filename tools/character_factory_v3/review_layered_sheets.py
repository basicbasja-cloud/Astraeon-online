#!/usr/bin/env python3
"""Build review-only GIFs, contact sheets, and continuity diagnostics.

This reads independently painted eight-direction sheets with variable frame
rows and never writes a runtime character package. A separately authored
`WeaponLight` sheet can be reviewed as a layer synchronized with BasicAttack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from import_layered_sheets import (
    ACTIONS,
    CELL,
    CORE_LAYERS,
    DIRECTIONS,
    SHEET,
    _load_sheet,
    _normalise,
    _preserve_cutout_registration,
)

BACKGROUND = (24, 32, 44, 255)
LAYER_ORDER = ("BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "CosmeticFX", "WeaponSlash", "WeaponLight")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frame_count(sheet: Image.Image) -> int:
    if sheet.width != SHEET or sheet.height < CELL * 2 or sheet.height % CELL:
        raise ValueError(f"Expected an eight-direction sheet with 160px cells: {sheet.size}")
    return sheet.height // CELL


def _composite(layers: dict[str, Image.Image]) -> Image.Image:
    first = next(iter(layers.values()))
    frame_count = _frame_count(first)
    if any(image.size != first.size for image in layers.values()):
        raise ValueError("Every layer must use the same direction and frame grid")
    sheet = Image.new("RGBA", first.size, (0, 0, 0, 0))
    for name in LAYER_ORDER:
        if name in layers:
            sheet.alpha_composite(layers[name])
    return sheet


def _bbox_and_mask(image: Image.Image) -> tuple[tuple[int, int, int, int] | None, np.ndarray]:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    mask = alpha > 8
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None, mask
    return (int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)), mask


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    union = int(np.logical_or(a, b).sum())
    return 1.0 if union == 0 else float(np.logical_and(a, b).sum() / union)


def _continuity(sheet: Image.Image, loop: bool) -> dict[str, Any]:
    frame_count = _frame_count(sheet)
    directions: dict[str, Any] = {}
    values: list[float] = []
    for direction_index, direction in enumerate(DIRECTIONS):
        frames: list[Image.Image] = []
        metrics: list[dict[str, Any]] = []
        masks: list[np.ndarray] = []
        for frame_index in range(frame_count):
            cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                               (direction_index + 1) * CELL, (frame_index + 1) * CELL))
            bbox, mask = _bbox_and_mask(cell)
            masks.append(mask)
            frames.append(cell)
            if bbox is None:
                metrics.append({"visible": False, "bbox": None, "height_px": 0, "bottom_y": None})
            else:
                metrics.append({"visible": True, "bbox": list(bbox),
                                "height_px": bbox[3] - bbox[1], "bottom_y": bbox[3] - 1})
        pairs = [(index, index + 1) for index in range(frame_count - 1)]
        if loop:
            pairs.append((frame_count - 1, 0))
        scores = [{"from": left, "to": right, "iou": round(_iou(masks[left], masks[right]), 4)}
                  for left, right in pairs]
        values.extend(item["iou"] for item in scores)
        heights = [item["height_px"] for item in metrics if item["visible"]]
        bottoms = [item["bottom_y"] for item in metrics if item["visible"]]
        directions[direction] = {
            "empty_frames": [index for index, item in enumerate(metrics) if not item["visible"]],
            "height_px_range": [min(heights, default=0), max(heights, default=0)],
            "bottom_y_range_px": max(bottoms, default=0) - min(bottoms, default=0),
            "silhouette_iou_mean": round(float(np.mean([item["iou"] for item in scores])), 4) if scores else 1.0,
            "silhouette_iou_min": round(min((item["iou"] for item in scores), default=1.0), 4),
            "pairs_below_0_88": [item for item in scores if item["iou"] < 0.88],
            "pairs": scores,
        }
    return {
        "frame_count": frame_count,
        "loop": loop,
        "gif_playback": "infinite_loop" if loop else "one_shot_hold_final",
        "mean_across_all_directions": round(float(np.mean(values)), 4) if values else 1.0,
        "minimum_pair": round(min(values, default=1.0), 4),
        "directions": directions,
        "interpretation": "IoU is a continuity warning for human review; it is not an art-quality score, and action poses can change silhouette intentionally.",
    }


def _review_gif(sheet: Image.Image, durations: list[int], target: Path, loop: bool) -> None:
    frame_count = _frame_count(sheet)
    if len(durations) != frame_count:
        raise ValueError(f"GIF needs {frame_count} durations; received {len(durations)}")
    frames: list[Image.Image] = []
    for frame_index in range(frame_count):
        row = Image.new("RGBA", (sheet.width, CELL), BACKGROUND)
        for direction_index in range(8):
            cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                               (direction_index + 1) * CELL, (frame_index + 1) * CELL))
            row.alpha_composite(cell, (direction_index * CELL, 0))
        # Keep the native 160px cell resolution so reviewers can judge edge
        # clarity, weapon shape, and layer seams without a preview downscale.
        frames.append(row.convert("RGB"))
    options: dict[str, Any] = {
        "save_all": True, "append_images": frames[1:], "duration": durations,
        "optimize": False, "disposal": 2,
    }
    if loop:
        options["loop"] = 0
    frames[0].save(target, **options)


def _layer_breakdown(layers: dict[str, Image.Image], target: Path, frame_index: int = 0) -> None:
    frame_count = _frame_count(next(iter(layers.values())))
    if not 0 <= frame_index < frame_count:
        raise ValueError(f"Breakdown frame {frame_index} outside 0..{frame_count - 1}")
    names = [name for name in LAYER_ORDER if name in layers] + ["ASSEMBLED"]
    cell_width, image_height, label_height = 160, 160, 30
    output = Image.new("RGB", (8 * cell_width, len(names) * (image_height + label_height)), (24, 32, 44))
    draw = ImageDraw.Draw(output)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    assembled = _composite(layers)
    y_source = frame_index * CELL
    for row_index, name in enumerate(names):
        source = assembled if name == "ASSEMBLED" else layers[name]
        y = row_index * (image_height + label_height)
        for direction_index in range(8):
            cell = source.crop((direction_index * CELL, y_source,
                               (direction_index + 1) * CELL, y_source + CELL))
            output.paste(cell, (direction_index * cell_width, y), cell)
        draw.text((4, y + image_height + 3), name, fill=(245, 238, 220), font=font)
    output.save(target, format="PNG", optimize=False)


def review_layered_sheets(
    repository: Path,
    input_root: Path,
    guide_root: Path | None,
    source_definition_path: Path,
    evidence_dir: Path,
    actions: list[str],
    reference_height: int = 112,
    preserve_cutout_registration: bool = False,
    weapon_light_sheet: Path | None = None,
) -> dict[str, Any]:
    if not actions or any(action not in ACTIONS for action in actions):
        raise ValueError(f"Select one or more of {', '.join(ACTIONS)}")
    layer_sheets: dict[str, dict[str, Image.Image]] = {}
    guide_sheets: dict[str, Image.Image] = {}
    inputs: dict[str, dict[str, dict[str, str]]] = {}
    used_weapon_light = False
    for action in actions:
        layer_sheets[action] = {}
        inputs[action] = {}
        for layer in CORE_LAYERS:
            path = input_root / layer / f"{action.lower()}.png"
            if not path.is_file():
                raise FileNotFoundError(f"Missing independently painted source sheet: {path}")
            layer_sheets[action][layer] = _load_sheet(path, layer, preserve_cutout_registration)
            inputs[action][layer] = {"file": str(path.relative_to(repository)), "sha256": _sha256(path)}
        automatic_weapon_light = input_root / "WeaponLight" / "basicattack.png"
        selected_weapon_light = weapon_light_sheet or (automatic_weapon_light if automatic_weapon_light.is_file() else None)
        use_weapon_light = action == "BasicAttack" and selected_weapon_light is not None
        fx_path = selected_weapon_light if use_weapon_light else input_root / "CosmeticFX" / f"{action.lower()}.png"
        if fx_path.is_file():
            effect_name = "WeaponLight" if use_weapon_light else "CosmeticFX"
            used_weapon_light = used_weapon_light or use_weapon_light
            layer_sheets[action][effect_name] = _load_sheet(fx_path, effect_name, preserve_cutout_registration)
            inputs[action][effect_name] = {
                "file": str(fx_path.relative_to(repository)),
                "sha256": _sha256(fx_path),
            }
        else:
            first = next(iter(layer_sheets[action].values()))
            layer_sheets[action]["CosmeticFX"] = Image.new("RGBA", first.size, (0, 0, 0, 0))
        if not preserve_cutout_registration:
            if guide_root is None:
                raise ValueError("A guide root is required unless cutout registration is preserved")
            guide_path = guide_root / f"{action.lower()}-guide.png"
            guide_sheets[action] = _load_sheet(guide_path, "BaseBody")

    if preserve_cutout_registration:
        normalized, normalization = _preserve_cutout_registration(layer_sheets, tuple(actions))
    else:
        normalized, normalization = _normalise(
            layer_sheets, guide_sheets, reference_height=reference_height, actions=tuple(actions))
    definition = json.loads(source_definition_path.read_text(encoding="utf-8"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    clips: dict[str, Any] = {}
    media: dict[str, Any] = {"gifs": {}, "layer_breakdowns": {}, "layer_breakdown_frames": {}}
    for action in actions:
        composite = _composite(normalized[action])
        clip = definition["clips"][action]
        frame_count = _frame_count(composite)
        clips[action] = _continuity(composite, bool(clip.get("loop")))
        duration_values = [int(value) for value in definition["clips"][action]["durations"]]
        if len(duration_values) != frame_count:
            raise ValueError(f"{action} has {frame_count} art frames but {len(duration_values)} durations")
        gif = evidence_dir / f"layered-v3-{action.lower()}-8-directions.gif"
        _review_gif(composite, duration_values, gif, bool(clip.get("loop")))
        media["gifs"][action] = gif.name
        breakdown = evidence_dir / f"layered-v3-{action.lower()}-layer-breakdown.png"
        effect_layer = normalized[action].get(
            "WeaponLight", normalized[action].get("WeaponSlash", normalized[action].get("CosmeticFX")))
        effect_alpha = np.asarray(effect_layer.getchannel("A"), dtype=np.uint8)
        effect_counts = [int(np.count_nonzero(effect_alpha[frame * CELL:(frame + 1) * CELL]))
                         for frame in range(frame_count)]
        breakdown_frame = max(range(frame_count), key=lambda frame: effect_counts[frame])
        _layer_breakdown(normalized[action], breakdown, breakdown_frame)
        media["layer_breakdowns"][action] = breakdown.name
        media["layer_breakdown_frames"][action] = breakdown_frame

    report = {
        "schema_version": 1,
        "review_status": "DIAGNOSTIC_ONLY_VISUAL_REVIEW_REQUIRED",
        "candidate": "swordsman-male-v3-layered-v2",
        "actions_reviewed": actions,
        "layers": list(CORE_LAYERS) + (["WeaponLight"] if used_weapon_light else ["CosmeticFX"]),
        "inputs": inputs,
        "normalization": normalization,
        "continuity": clips,
        "review_media": media,
        "warnings": [
            "Review-only output; no runtime package is created or changed.",
            "Generated art still needs visual review for material errors, hair and face identity, alpha fringes, layer seams, foot contact, and natural motion.",
            "A missing CosmeticFX or WeaponLight sheet stays transparent in this preview.",
        ],
    }
    target = evidence_dir / "layered-v3-review-report.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--guide-root", type=Path)
    parser.add_argument("--source-definition", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--actions", nargs="+", required=True, choices=ACTIONS)
    parser.add_argument("--reference-height", type=int, default=112)
    parser.add_argument("--weapon-light-sheet", type=Path,
                        help="Separately authored WeaponLight sheet for BasicAttack review")
    parser.add_argument("--preserve-cutout-registration", action="store_true",
                        help="Review exact pixel-labelled cutouts without alpha cleanup or guide fitting")
    args = parser.parse_args()
    repository = args.repository.resolve()

    def resolve(path: Path) -> Path:
        return (repository / path).resolve() if not path.is_absolute() else path.resolve()

    if args.guide_root is None and not args.preserve_cutout_registration:
        parser.error("--guide-root is required unless --preserve-cutout-registration is set")
    inputs = (resolve(args.input_root), None if args.guide_root is None else resolve(args.guide_root))
    if any(path is not None and not path.is_relative_to(repository) for path in inputs):
        raise ValueError("Input and guide paths must remain inside the repository")
    weapon_light_sheet = None if args.weapon_light_sheet is None else resolve(args.weapon_light_sheet)
    if weapon_light_sheet is not None and not weapon_light_sheet.is_relative_to(repository):
        raise ValueError("WeaponLight input must remain inside the repository")
    result = review_layered_sheets(
        repository, inputs[0], inputs[1], resolve(args.source_definition),
        resolve(args.evidence_dir), args.actions, args.reference_height,
        args.preserve_cutout_registration, weapon_light_sheet)
    print(json.dumps({"review_status": result["review_status"],
                      "actions_reviewed": result["actions_reviewed"],
                      "review_media": result["review_media"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
