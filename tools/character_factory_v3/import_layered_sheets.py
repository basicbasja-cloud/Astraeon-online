#!/usr/bin/env python3
"""Import genuinely separate transparent layer sheets into the V3 sprite runtime.

Input layout: <input-root>/<Layer>/<Action>.png. Each input has eight direction
columns and a variable number of chronological frame rows. The importer can apply
one shared per-pose transform across parts, or preserve exact pixel-labelled
cutouts from a full-character master with --preserve-cutout-registration. A
reviewed `WeaponLight/basicattack.png` is imported as its own optional runtime
layer. Rejected legacy `WeaponSlash` sources are ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

DIRECTIONS = ("S", "SW", "W", "NW", "N", "NE", "E", "SE")
ACTIONS = ("Idle", "Walk", "BasicAttack")
CORE_LAYERS = ("BaseBody", "Hair", "Outfit", "Weapon", "BackAccessory")
CELL = 160
SHEET = CELL * len(DIRECTIONS)
ALPHA_THRESHOLD = 8
SHEET_ALPHA_THRESHOLD = 128
FX_ALPHA_THRESHOLD = 24

PARTS = {
    "base-body-v1": ("Body", "BaseBody", "swordsman-base-body-v1"),
    "silver-hair-v1": ("Hair", "Hair", "silver-swept-hair-v1"),
    "golden-outfit-v1": ("Outfit", "Outfit", "golden-swordsman-outfit-v1"),
    "steel-sword-v1": ("Weapon", "Weapon", "bronze-hilt-steel-sword-v1"),
    "headgear-empty": ("Headgear", None, "no-headgear"),
    "golden-cloak-v1": ("Back", "BackAccessory", "gold-scarf-cloak-v1"),
    "empty-back-accessory": ("Back", None, "no-back-accessory"),
    "golden-sword-trail-v1": ("FX", "WeaponLight", "golden-sword-trail-v1"),
    "empty-cosmetic-fx": ("FX", None, "no-combat-effect"),
}


def _frame_count(sheet: Image.Image) -> int:
    if sheet.width != SHEET or sheet.height < CELL * 2 or sheet.height % CELL:
        raise ValueError(f"Expected eight {CELL}px columns and at least two frame rows: {sheet.size}")
    return sheet.height // CELL


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean_cell(image: Image.Image, layer: str) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    source_alpha = rgba[:, :, 3]
    threshold = FX_ALPHA_THRESHOLD if layer in ("CosmeticFX", "WeaponLight") else SHEET_ALPHA_THRESHOLD
    alpha = np.clip((source_alpha.astype(np.float32) - threshold) * (255.0 / (255 - threshold)), 0.0, 255.0).astype(np.uint8)
    solid = alpha > ALPHA_THRESHOLD
    if not np.any(solid):
        rgba[:, :, 3] = 0
        return Image.fromarray(rgba, mode="RGBA")
    labels, count = ndimage.label(solid, structure=np.ones((3, 3), dtype=bool))
    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    sizes[0] = 0
    largest = int(sizes.max())
    ratio = 0.003 if layer in ("CosmeticFX", "WeaponLight") else 0.012
    minimum = max(5 if layer in ("CosmeticFX", "WeaponLight") else 12, int(largest * ratio))
    keep_ids = np.flatnonzero(sizes >= minimum)
    keep = np.isin(labels, keep_ids) & solid
    rgba[:, :, 3] = np.where(keep, alpha, 0).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def _load_sheet(path: Path, layer: str, preserve_source_alpha: bool = False) -> Image.Image:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    if image.getchannel("A").getextrema()[0] != 0:
        raise ValueError(f"Layer sheet must retain transparent pixels: {path}")
    source_cell_width = image.width / len(DIRECTIONS)
    source_frame_count = round(image.height / source_cell_width) if source_cell_width else 0
    if (source_cell_width < 64 or source_frame_count < 2
            or abs(image.height - source_cell_width * source_frame_count) > 1.0):
        raise ValueError(f"Expected an eight-column sheet with uniform square cells: {path} ({image.size})")
    target_size = (SHEET, source_frame_count * CELL)
    if preserve_source_alpha and image.size != target_size:
        raise ValueError(f"Cutout sheets must preserve the exact {target_size} source grid: {path} ({image.size})")
    if image.size != target_size:
        image = image.resize(target_size, Image.Resampling.LANCZOS)
    if preserve_source_alpha:
        return image
    clean = Image.new("RGBA", target_size, (0, 0, 0, 0))
    for row in range(source_frame_count):
        for col in range(len(DIRECTIONS)):
            box = (col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL)
            clean.alpha_composite(_clean_cell(image.crop(box), layer), (box[0], box[1]))
    return clean


def _preserve_cutout_registration(
    layer_sheets: dict[str, dict[str, Image.Image]],
    actions: tuple[str, ...],
) -> tuple[dict[str, dict[str, Image.Image]], dict[str, Any]]:
    heights: list[int] = []
    frame_records = []
    frame_counts = {action: _frame_count(next(iter(layer_sheets[action].values()))) for action in actions}
    for action in actions:
        frame_count = frame_counts[action]
        for layer, sheet in layer_sheets[action].items():
            if _frame_count(sheet) != frame_count:
                raise ValueError(f"Frame-count mismatch in {action}/{layer}")
        for frame_index in range(frame_count):
            for direction_index, direction in enumerate(DIRECTIONS):
                box = (direction_index * CELL, frame_index * CELL,
                       (direction_index + 1) * CELL, (frame_index + 1) * CELL)
                cells = {layer: sheet.crop(box) for layer, sheet in layer_sheets[action].items()}
                bounds = _alpha_union([cells[layer] for layer in CORE_LAYERS]).getbbox()
                if bounds is None:
                    raise ValueError(f"Empty cutout master pose: {action}/{direction}/{frame_index}")
                height = bounds[3] - bounds[1]
                heights.append(height)
                frame_records.append({"action": action, "direction": direction,
                                      "frame_index": frame_index, "source_bbox": list(bounds),
                                      "source_height_px": height, "source_bottom_y": bounds[3] - 1})
    reference_height = float(statistics.median(heights))
    if reference_height < 40 or reference_height > CELL:
        raise ValueError(f"Cutout master character height is outside the usable range ({reference_height:.1f}px)")
    preserved = {action: {layer: sheet.copy() for layer, sheet in layer_sheets[action].items()}
                 for action in actions}
    return preserved, {
        "layout": "directions_are_columns_frames_are_rows",
        "uniform_scale": 1.0,
        "target_reference_height_px": int(round(reference_height)),
        "source_guide_median_height_px": None,
        "registration_policy": "preserve full-master pixels, alpha, and frame coordinates; no scale, translation, crop, or alpha cleanup",
        "frame_counts": frame_counts,
        "frame_count": len(frame_records),
        "frames": frame_records,
    }


def _bbox(image: Image.Image, threshold: int = ALPHA_THRESHOLD) -> tuple[int, int, int, int] | None:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    return Image.fromarray(np.where(alpha > threshold, 255, 0).astype(np.uint8), mode="L").getbbox()


def _alpha_union(images: list[Image.Image]) -> Image.Image:
    alpha = np.zeros((CELL, CELL), dtype=np.uint8)
    for image in images:
        alpha = np.maximum(alpha, np.asarray(image.getchannel("A"), dtype=np.uint8))
    return Image.fromarray(alpha, mode="L")


def _fit_frame(
    cells: dict[str, Image.Image],
    guide_bbox: tuple[float, float, float, float],
    scale: float,
) -> tuple[dict[str, Image.Image], dict[str, Any]]:
    core = [cells[layer] for layer in CORE_LAYERS]
    union = _alpha_union(core)
    source_box = union.getbbox()
    if source_box is None:
        raise ValueError("A visible layered character and guide are required for every action/direction/frame")
    sx0, sy0, sx1, sy1 = source_box
    gx0, gy0, gx1, gy1 = guide_bbox
    target_cx = (gx0 + gx1) / 2.0
    target_bottom = float(gy1)
    left = round(target_cx - ((sx0 + sx1) / 2.0) * scale)
    top = round(target_bottom - sy1 * scale)
    size = (max(1, round(CELL * scale)), max(1, round(CELL * scale)))
    fitted: dict[str, Image.Image] = {}
    clipping: dict[str, bool] = {}
    for layer, original in cells.items():
        resized = original.resize(size, Image.Resampling.LANCZOS)
        expanded = Image.new("RGBA", (CELL * 4, CELL * 4), (0, 0, 0, 0))
        expanded.alpha_composite(resized, (CELL + left, CELL + top))
        crop = expanded.crop((CELL, CELL, CELL * 2, CELL * 2))
        before = expanded.crop((0, 0, CELL, CELL * 4))
        # The margin test below is based on the transformed alpha outside the
        # target cell, including both horizontal sides and vertical margins.
        outside = expanded.copy()
        draw = ImageDraw.Draw(outside)
        draw.rectangle((CELL, CELL, CELL * 2 - 1, CELL * 2 - 1), fill=(0, 0, 0, 0))
        clipping[layer] = _bbox(outside) is not None
        fitted[layer] = crop
    return fitted, {
        "source_union_bbox": list(source_box),
        "guide_bbox": [round(value, 3) for value in guide_bbox],
        "scale": round(scale, 6),
        "translation": [left, top],
        "clipped_layers": [layer for layer, clipped in clipping.items() if clipped],
    }


def _normalise(
    layer_sheets: dict[str, dict[str, Image.Image]],
    guides: dict[str, Image.Image],
    reference_height: int = 112,
    actions: tuple[str, ...] = ACTIONS,
) -> tuple[dict[str, dict[str, Image.Image]], dict[str, Any]]:
    if reference_height <= 0 or reference_height > CELL:
        raise ValueError(f"reference_height must be within the {CELL}px runtime cell")
    records: dict[tuple[str, int, int], dict[str, Image.Image]] = {}
    guide_boxes: dict[tuple[str, int, int], tuple[int, int, int, int]] = {}
    guide_heights: list[int] = []
    frame_counts = {action: _frame_count(next(iter(layer_sheets[action].values()))) for action in actions}
    for action in actions:
        frame_count = frame_counts[action]
        for layer, sheet in layer_sheets[action].items():
            if _frame_count(sheet) != frame_count:
                raise ValueError(f"Frame-count mismatch in {action}/{layer}")
        if _frame_count(guides[action]) != frame_count:
            raise ValueError(f"Guide frame-count mismatch in {action}")
        for frame_index in range(frame_count):
            for direction_index in range(len(DIRECTIONS)):
                key = (action, frame_index, direction_index)
                box = (direction_index * CELL, frame_index * CELL,
                       (direction_index + 1) * CELL, (frame_index + 1) * CELL)
                cells = {layer: sheet.crop(box) for layer, sheet in layer_sheets[action].items()}
                union_box = _alpha_union([cells[layer] for layer in CORE_LAYERS]).getbbox()
                guide_box = _bbox(guides[action].crop(box))
                if union_box is None or guide_box is None:
                    raise ValueError(f"Missing visible character or guide pixels: {action}/{DIRECTIONS[direction_index]}/{frame_index}")
                source_height = union_box[3] - union_box[1]
                guide_height = guide_box[3] - guide_box[1]
                if source_height <= 0 or guide_height <= 0:
                    raise ValueError(f"Invalid frame height for {action}/{DIRECTIONS[direction_index]}/{frame_index}")
                guide_heights.append(guide_height)
                records[key] = cells
                guide_boxes[key] = guide_box
    guide_reference = float(statistics.median(guide_heights))
    guide_scale = reference_height / guide_reference
    target_boxes: dict[tuple[str, int, int], tuple[float, float, float, float]] = {}
    scales: list[float] = []
    for key, cells in records.items():
        source_box = _alpha_union([cells[layer] for layer in CORE_LAYERS]).getbbox()
        guide_box = guide_boxes[key]
        gx0, gy0, gx1, gy1 = guide_box
        source_height = source_box[3] - source_box[1]
        target_height = (gy1 - gy0) * guide_scale
        target_width = (gx1 - gx0) * guide_scale
        target_cx = (gx0 + gx1) / 2.0
        target_bottom = float(gy1)
        target_boxes[key] = (target_cx - target_width / 2.0, target_bottom - target_height,
                             target_cx + target_width / 2.0, target_bottom)
        scales.append(target_height / source_height)
    scale = float(statistics.median(scales))
    if not 0.4 <= scale <= 1.8:
        raise ValueError(f"Layer sheets and guide have incompatible scale ({scale:.3f})")

    normalized = {action: {layer: Image.new("RGBA", (SHEET, frame_counts[action] * CELL), (0, 0, 0, 0))
                           for layer in layer_sheets[action]} for action in actions}
    frame_records = []
    for action in actions:
        for frame_index in range(frame_counts[action]):
            for direction_index, direction in enumerate(DIRECTIONS):
                key = (action, frame_index, direction_index)
                fitted, record = _fit_frame(records[key], target_boxes[key], scale)
                if record["clipped_layers"]:
                    raise ValueError(f"Layer content leaves the runtime cell at {action}/{direction}/{frame_index}: {record['clipped_layers']}")
                for layer, cell in fitted.items():
                    normalized[action][layer].alpha_composite(
                        cell, (direction_index * CELL, frame_index * CELL))
                frame_records.append({"action": action, "direction": direction,
                                      "frame_index": frame_index, **record})
    return normalized, {
        "layout": "directions_are_columns_frames_are_rows",
        "uniform_scale": round(scale, 6),
        "target_reference_height_px": reference_height,
        "source_guide_median_height_px": guide_reference,
        "registration_policy": "one transform shared by all part layers in each pose; center and foot baseline match the corresponding structural guide",
        "frame_counts": frame_counts,
        "frame_count": len(frame_records),
        "frames": frame_records,
    }


def _strip(sheet: Image.Image) -> Image.Image:
    frame_count = _frame_count(sheet)
    strip = Image.new("RGBA", (CELL * frame_count, CELL * len(DIRECTIONS)), (0, 0, 0, 0))
    for frame_index in range(frame_count):
        for direction_index in range(len(DIRECTIONS)):
            cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                               (direction_index + 1) * CELL, (frame_index + 1) * CELL))
            strip.alpha_composite(cell, (frame_index * CELL, direction_index * CELL))
    return strip


def _blank_strip(count: int) -> Image.Image:
    return Image.new("RGBA", (CELL * count, CELL * len(DIRECTIONS)), (0, 0, 0, 0))


def _pose_strip(sheet: Image.Image, count: int, frame_index: int = 0) -> Image.Image:
    strip = _blank_strip(count)
    for direction_index in range(len(DIRECTIONS)):
        cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                           (direction_index + 1) * CELL, (frame_index + 1) * CELL))
        for index in range(count):
            strip.alpha_composite(cell, (index * CELL, direction_index * CELL))
    return strip


def _write_review_media(
    sheets: dict[str, dict[str, Image.Image]],
    definition: dict[str, Any],
    evidence: Path,
) -> dict[str, str]:
    evidence.mkdir(parents=True, exist_ok=True)
    layer_order = ("BackAccessory", "BaseBody", "Outfit", "Hair", "Weapon", "CosmeticFX", "WeaponLight")
    composites: dict[str, Image.Image] = {}
    for action in ACTIONS:
        frame_count = _frame_count(next(iter(sheets[action].values())))
        output = Image.new("RGBA", (SHEET, frame_count * CELL), (0, 0, 0, 0))
        for layer in layer_order:
            if layer in sheets[action]:
                output.alpha_composite(sheets[action][layer])
        composites[action] = output
    gifs: dict[str, str] = {}
    for action, sheet in composites.items():
        clip = definition["clips"][action]
        frame_count = _frame_count(sheet)
        if len(clip["durations"]) != frame_count:
            raise ValueError(f"{action} has {frame_count} art frames but {len(clip['durations'])} durations")
        frames = []
        for frame_index in range(frame_count):
            line = Image.new("RGBA", (SHEET, CELL), (24, 32, 44, 255))
            for direction_index in range(8):
                cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                                   (direction_index + 1) * CELL, (frame_index + 1) * CELL))
                line.alpha_composite(cell, (direction_index * CELL, 0))
            frames.append(line.convert("RGB"))
        durations = [int(value) for value in clip["durations"]]
        target = evidence / f"layered-v3-{action.lower()}-8-directions.gif"
        save_options = {"save_all": True, "append_images": frames[1:],
                        "duration": durations, "optimize": False, "disposal": 2}
        if clip.get("loop"):
            save_options["loop"] = 0
        frames[0].save(target, **save_options)
        gifs[action] = target.name

    attack = composites["BasicAttack"]
    contact_events = [event for event in definition["clips"]["BasicAttack"].get("events", [])
                       if event.get("name", "").lower() == "contact" or event.get("phase") == "contact"]
    contact_index = int(contact_events[0]["frameIndex"]) if contact_events else 4
    attack_count = _frame_count(attack)
    contact_columns = 4
    contact_rows = math.ceil(attack_count / contact_columns)
    sheet = Image.new("RGB", (contact_columns * 190, contact_rows * 210), (24, 32, 44))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    for frame_index in range(attack_count):
        x, y = (frame_index % contact_columns) * 190, (frame_index // contact_columns) * 210
        cell = attack.crop((0, frame_index * CELL, CELL, (frame_index + 1) * CELL))
        sheet.paste(cell, (x + 15, y + 6), cell)
        label = f"Frame {frame_index:02d}" + (" · CONTACT" if frame_index == contact_index else "")
        draw.text((x + 10, y + 170), label, fill=(245, 238, 220), font=font)
    contact_path = evidence / "layered-v3-basicattack-contact-sheet.png"
    sheet.save(contact_path, format="PNG", optimize=False)
    return {"gifs": gifs, "basic_attack_contact_sheet": contact_path.name}


def _build_definition(
    source_definition: dict[str, Any], candidate_id: str,
    normalized: dict[str, dict[str, Image.Image]], output_root: Path,
    reference_height: int = 112,
) -> Path:
    definition = json.loads(json.dumps(source_definition))
    definition["characterId"] = candidate_id
    definition["canvas"]["referenceHeight"] = reference_height
    definition["tags"] = ["DEV_ONLY", "PLACEHOLDER", "NOT_FINAL_ART", "LAYERED_ART_CANDIDATE", "OWNER_APPROVAL_PENDING"]
    definition["source"] = {
        "status": "DEV_ONLY",
        "reference": "authoring/characters/factory-v3/identities/swordsman_identity_v1.json",
        "approvedBy": None,
        "camera": "CAM_FantasySprite; orthographic; 320x320; root pixel 160,264",
        "handedness": "right",
        "designLocks": [
            "Independent transparent BaseBody, Hair, Outfit, Weapon, Headgear, BackAccessory, and WeaponLight parts",
            "Default cosmetic is the separate golden scarf/cloak; a fully transparent no-cloak variant is available",
            "WeaponLight is a separate transparent source layer synchronized to the attack pose and mapped to the runtime FX slot",
            "Owner-supplied high-detail images set visual direction; owner review remains pending",
        ],
    }
    definition["slots"]["FX"] = "WeaponLight"
    definition["defaultParts"] = {
        "Body": "base-body-v1",
        "Hair": "silver-hair-v1",
        "Outfit": "golden-outfit-v1",
        "Weapon": "steel-sword-v1",
        "Headgear": "headgear-empty",
        "Back": "golden-cloak-v1",
        "FX": "golden-sword-trail-v1",
    }
    definition["drawOrder"] = ["Back", "Body", "Outfit", "Hair", "Weapon", "FX", "Headgear"]

    definitions = {
        "base-body-v1": ("Body", "swordsman-base-body-v1", "BaseBody"),
        "silver-hair-v1": ("Hair", "silver-swept-hair-v1", "Hair"),
        "golden-outfit-v1": ("Outfit", "golden-swordsman-outfit-v1", "Outfit"),
        "steel-sword-v1": ("Weapon", "bronze-hilt-steel-sword-v1", "Weapon"),
        "headgear-empty": ("Headgear", "no-headgear", None),
        "golden-cloak-v1": ("Back", "gold-scarf-cloak-v1", "BackAccessory"),
        "empty-back-accessory": ("Back", "no-back-accessory", None),
        "golden-sword-trail-v1": ("FX", "golden-sword-trail-v1", "WeaponLight"),
        "empty-cosmetic-fx": ("FX", "no-combat-effect", None),
    }
    parts: dict[str, Any] = {}
    for part_id, (slot, cosmetic_id, layer) in definitions.items():
        part_tags = ["INDEPENDENT_ART_LAYER", "OWNER_APPROVAL_PENDING"] if layer else ["TRANSPARENT_OPTIONAL_LAYER"]
        parts[part_id] = {"slot": slot, "cosmeticId": cosmetic_id, "tags": part_tags, "frames": {}}
    definition["parts"] = parts
    definition["atlases"] = {}
    staging = output_root / "runtime-source"
    for part_id, (slot, _, layer) in definitions.items():
        for action, clip in definition["clips"].items():
            count = len(clip["durations"])
            if action in ACTIONS and _frame_count(next(iter(normalized[action].values()))) != count:
                raise ValueError(f"{action} art frame-count does not match its {count}-frame timeline")
            target = staging / "parts" / part_id / action / "strip.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            if layer is None:
                strip = _blank_strip(count)
            elif action in ACTIONS:
                strip = _strip(normalized[action][layer])
            else:
                strip = _pose_strip(normalized["Idle"][layer], count)
            strip.save(target, format="PNG", optimize=False)
    definition_path = staging / "sprite-definition.json"
    definition_path.parent.mkdir(parents=True, exist_ok=True)
    definition_path.write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    packer = Path(__file__).resolve().parents[2] / "tools" / "pack-modular-sprites.py"
    repository = Path(__file__).resolve().parents[2]
    subprocess.run([sys.executable, str(packer), "--definition", str(definition_path), "--sources", str(staging),
                    "--repository", str(repository), "--deduplicate"], cwd=repository, check=True,
                   capture_output=True, text=True)
    return repository / "assets" / "characters" / candidate_id / "sprite.json"


def import_layered_sheets(
    repository: Path,
    input_root: Path,
    guide_root: Path | None,
    source_definition_path: Path,
    candidate_id: str,
    output_root: Path,
    evidence_dir: Path,
    reference_height: int = 112,
    preserve_cutout_registration: bool = False,
) -> dict[str, Any]:
    layer_sheets: dict[str, dict[str, Image.Image]] = {action: {} for action in ACTIONS}
    source_files: dict[str, dict[str, dict[str, str]]] = {action: {} for action in ACTIONS}
    for action in ACTIONS:
        for layer in CORE_LAYERS:
            path = input_root / layer / f"{action.lower()}.png"
            if not path.is_file():
                raise FileNotFoundError(f"Missing independently painted source sheet: {path}")
            layer_sheets[action][layer] = _load_sheet(path, layer, preserve_cutout_registration)
            source_files[action][layer] = {"file": str(path.relative_to(repository)), "sha256": sha256(path)}
        light_path = input_root / "WeaponLight" / f"{action.lower()}.png"
        use_weapon_light = action == "BasicAttack" and light_path.is_file()
        if use_weapon_light:
            layer_sheets[action]["WeaponLight"] = _load_sheet(
                light_path, "WeaponLight", preserve_cutout_registration)
            source_files[action]["WeaponLight"] = {
                "file": str(light_path.relative_to(repository)),
                "sha256": sha256(light_path),
            }
        else:
            frame_count = _frame_count(next(iter(layer_sheets[action].values())))
            layer_sheets[action]["WeaponLight"] = Image.new(
                "RGBA", (SHEET, frame_count * CELL), (0, 0, 0, 0))

    guides = {} if preserve_cutout_registration else {
        action: _load_sheet(guide_root / f"{action.lower()}-guide.png", "BaseBody") for action in ACTIONS
    }
    source_definition = json.loads(source_definition_path.read_text(encoding="utf-8"))
    if preserve_cutout_registration:
        normalized, report = _preserve_cutout_registration(layer_sheets, ACTIONS)
        reference_height = int(report["target_reference_height_px"])
    else:
        normalized, report = _normalise(layer_sheets, guides, reference_height)
    runtime_path = _build_definition(source_definition, candidate_id, normalized, output_root, reference_height)
    media = _write_review_media(normalized, source_definition, (repository / evidence_dir).resolve())
    audit_script = Path(__file__).resolve().with_name("audit_sprite_candidate.py")
    audit_path = (repository / evidence_dir / "layered-v3-visual-audit.json").resolve()
    audit_result = subprocess.run([sys.executable, str(audit_script), str(runtime_path), "--output", str(audit_path)],
                                  cwd=repository, check=True, capture_output=True, text=True)
    validator = repository / "tools/character_factory_v3/validate_runtime_package.cjs"
    validation = subprocess.run(["node", str(validator), str(runtime_path)], cwd=repository, check=True,
                                capture_output=True, text=True)
    job = {
        "schema_version": 1,
        "candidate": candidate_id,
        "provider": "OpenAI ImageGen",
        "status": "LAYERED_ART_CANDIDATE_OWNER_APPROVAL_PENDING",
        "source_definition": str(source_definition_path.relative_to(repository)),
        "input_sources": source_files,
        "source_motion_license": "Mesh2Motion CC0 source clips are pose/timing guides; no motion asset is sent to image generation.",
        "output_license_note": "Generated images follow the image provider's applicable terms; no independent CC0 claim is made.",
        "normalization": report,
        "modularity": {
            "status": "SEPARATE_LAYER_INPUTS",
            "layers": [*CORE_LAYERS, "WeaponLight"],
            "effect_layer": "Reviewed WeaponLight source mapped to the independent runtime FX slot; missing attack effect remains transparent",
            "ignored_rejected_weapon_slash_layers": [
                str(path.relative_to(repository))
                for path in sorted((input_root / "WeaponSlash").glob("*.png"))
            ] if (input_root / "WeaponSlash").is_dir() else [],
            "ignored_basicattack_cosmetic_fx": (
                str((input_root / "CosmeticFX" / "basicattack.png").relative_to(repository))
                if (input_root / "CosmeticFX" / "basicattack.png").is_file() else None
            ),
            "registration_policy": report["registration_policy"],
            "cloak_default": "golden-cloak-v1",
            "no_cloak_variant": "empty-back-accessory",
            "composite_source_accepted": False,
            "owner_approval": False,
        },
        "runtime_definition": str(runtime_path.relative_to(repository)),
        "review_media": media,
        "visual_audit": json.loads(audit_path.read_text(encoding="utf-8")),
        "runtime_validation": json.loads(validation.stdout),
    }
    (output_root / "job.json").write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")
    return job


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--guide-root", type=Path)
    parser.add_argument("--source-definition", type=Path, required=True)
    parser.add_argument("--candidate-id", default="swordsman-male-v3-layered")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--reference-height", type=int, default=112)
    parser.add_argument("--preserve-cutout-registration", action="store_true",
                        help="Preserve pixel-labelled master cutouts without alpha cleanup or guide fitting")
    args = parser.parse_args()
    repository = args.repository.resolve()
    resolve = lambda path: (repository / path).resolve() if not path.is_absolute() else path.resolve()
    if args.guide_root is None and not args.preserve_cutout_registration:
        parser.error("--guide-root is required unless --preserve-cutout-registration is set")
    for path in (args.input_root, args.guide_root):
        if path is None:
            continue
        resolved = resolve(path)
        if not resolved.is_relative_to(repository):
            raise ValueError(f"Input must be preserved inside the repository: {resolved}")
    result = import_layered_sheets(
        repository, resolve(args.input_root), None if args.guide_root is None else resolve(args.guide_root),
        resolve(args.source_definition), args.candidate_id, resolve(args.output_root),
        args.evidence_dir, args.reference_height, args.preserve_cutout_registration,
    )
    print(json.dumps({"candidate": result["candidate"], "status": result["status"],
                      "runtime_definition": result["runtime_definition"],
                      "review_media": result["review_media"], "modularity": result["modularity"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Layered-sheet import failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
