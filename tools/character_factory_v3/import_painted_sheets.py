#!/usr/bin/env python3
"""Normalize coherent AI-painted 8x8 sheets and package a review-only V3 sprite.

Inputs use ImageGen's layout: eight directions across columns, chronological
frames down rows. One scale is measured across the complete 3-action set and
applied uniformly. Each cell is translated to the corresponding guide bounds
so all painted actions share the established pose/root contract.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
ACTIONS = ["Idle", "Walk", "BasicAttack"]
CELL = 160
SHEET = CELL * len(DIRECTIONS)
ALPHA_THRESHOLD = 128
GEOMETRY_ALPHA_THRESHOLD = 8
RETIRED_CANDIDATES = frozenset({"swordsman-male-v3", "swordsman-male-v3-painted", "swordsman-male-v3-painted-v2"})
EMPTY_PARTS = {
    "empty-hair": "Hair",
    "empty-outfit": "Outfit",
    "empty-weapon": "Weapon",
    "empty-headgear": "Headgear",
    "empty-back-accessory": "Back",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_grid(path: Path, *, alpha_threshold: int = ALPHA_THRESHOLD) -> Image.Image:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    if image.width != image.height or image.width < 8 * 64:
        raise ValueError(f"Expected a square 8x8 sheet at useful resolution: {path} ({image.size})")
    # Remove generated background haze before resampling, then let LANCZOS
    # create clean antialiasing around the opaque sprite edges.
    alpha = np.asarray(image.getchannel("A"), dtype=np.float32)
    alpha = np.clip((alpha - alpha_threshold) * (255.0 / (255 - alpha_threshold)), 0.0, 255.0).astype(np.uint8)
    image.putalpha(Image.fromarray(alpha, mode="L"))
    # Normalize the complete sheet as one image. Never resize cells independently.
    return image.resize((SHEET, SHEET), Image.Resampling.LANCZOS)


def _bbox(image: Image.Image, threshold: int = 0) -> tuple[int, int, int, int] | None:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    mask = Image.fromarray(np.where(alpha > threshold, 255, 0).astype(np.uint8), mode="L")
    return mask.getbbox()


def _isolate_main_subject(cell: Image.Image) -> Image.Image:
    """Drop detached fragments that ImageGen sometimes spills from a neighbor cell."""
    alpha = np.asarray(cell.getchannel("A"), dtype=np.uint8)
    solid = alpha > GEOMETRY_ALPHA_THRESHOLD
    if not solid.any():
        return Image.new("RGBA", cell.size, (0, 0, 0, 0))
    # A small dilation reconnects antialiased parts such as a hand-held sword,
    # while a detached boot or fragment from the adjacent row remains separate.
    expanded = ndimage.binary_dilation(solid, structure=np.ones((9, 9), dtype=bool))
    labels, count = ndimage.label(expanded, structure=np.ones((3, 3), dtype=bool))
    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    sizes[0] = 0
    main_label = int(np.argmax(sizes))
    keep = solid & (labels == main_label)
    cleaned = cell.copy()
    cleaned.putalpha(Image.fromarray(np.where(keep, alpha, 0).astype(np.uint8), mode="L"))
    return cleaned


def _guide_silhouette_mask(cell: Image.Image, dilation: int = 13) -> Image.Image:
    alpha = np.asarray(cell.getchannel("A"), dtype=np.uint8)
    mask = Image.fromarray(np.where(alpha > GEOMETRY_ALPHA_THRESHOLD, 255, 0).astype(np.uint8), mode="L")
    return mask.filter(ImageFilter.MaxFilter(dilation))


def prepare_painted_sheets(
    painted_paths: dict[str, Path],
    guide_paths: dict[str, Path],
    output_dir: Path,
    *,
    alpha_threshold: int = ALPHA_THRESHOLD,
) -> tuple[dict[str, Image.Image], dict[str, Any]]:
    """Clean backgrounds, choose one global scale, and align every cell to its guide."""
    if not 0 <= alpha_threshold < 255:
        raise ValueError("Alpha threshold must be in 0..254")
    if set(painted_paths) != set(ACTIONS) or set(guide_paths) != set(ACTIONS):
        raise ValueError(f"Paint and guide inputs must cover exactly {ACTIONS}")
    painted = {action: _load_grid(painted_paths[action], alpha_threshold=alpha_threshold) for action in ACTIONS}
    for action in ACTIONS:
        cleaned = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
        for frame_index in range(8):
            for direction_index in range(8):
                tile = (direction_index * CELL, frame_index * CELL,
                        (direction_index + 1) * CELL, (frame_index + 1) * CELL)
                cleaned.alpha_composite(_isolate_main_subject(painted[action].crop(tile)), (tile[0], tile[1]))
        painted[action] = cleaned
    guides: dict[str, Image.Image] = {}
    for action in ACTIONS:
        with Image.open(guide_paths[action]) as opened:
            guide = opened.convert("RGBA")
        if guide.size != (SHEET, SHEET):
            raise ValueError(f"Guide must be {SHEET}x{SHEET}: {guide_paths[action]} ({guide.size})")
        guides[action] = guide

    measurements: dict[tuple[str, int, int], tuple[tuple[int, int, int, int], tuple[int, int, int, int]]] = {}
    source_heights: list[int] = []
    painted_heights: list[int] = []
    for action in ACTIONS:
        for frame_index in range(8):
            for direction_index in range(8):
                tile = (direction_index * CELL, frame_index * CELL,
                        (direction_index + 1) * CELL, (frame_index + 1) * CELL)
                paint_box = _bbox(painted[action].crop(tile), threshold=GEOMETRY_ALPHA_THRESHOLD)
                guide_box = _bbox(guides[action].crop(tile), threshold=GEOMETRY_ALPHA_THRESHOLD)
                if not paint_box:
                    raise ValueError(f"Painted character missing: {action}/{DIRECTIONS[direction_index]}/{frame_index}")
                if not guide_box:
                    raise ValueError(f"Guide character missing: {action}/{DIRECTIONS[direction_index]}/{frame_index}")
                measurements[(action, frame_index, direction_index)] = (paint_box, guide_box)
                source_heights.append(guide_box[3] - guide_box[1])
                painted_heights.append(paint_box[3] - paint_box[1])

    # One scale for all 192 cells avoids action- and frame-specific size wobble.
    uniform_scale = statistics.median(source_heights) / statistics.median(painted_heights)
    if not 0.45 <= uniform_scale <= 1.15:
        raise ValueError(f"Painted scale is far outside the guide contract: {uniform_scale:.3f}")
    normalized: dict[str, Image.Image] = {}
    report: dict[str, Any] = {
        "passed": True,
        "layout": "directions_are_columns_frames_are_rows",
        "directions": DIRECTIONS,
        "actions": ACTIONS,
        "cell_size": CELL,
        "sheet_size": [SHEET, SHEET],
        "alpha_threshold": alpha_threshold,
        "geometry_alpha_threshold": GEOMETRY_ALPHA_THRESHOLD,
        "subject_cleanup": "keep largest 8-connected subject after a 4px reconnection dilation; removes detached neighboring-cell fragments",
        "silhouette_cleanup": "clip each painted frame to its matching guide alpha silhouette dilated by 6px; removes far fringe/strays while allowing small pose and costume edge differences",
        "uniform_character_scale": round(uniform_scale, 6),
        "scale_policy": "one shared scale across all 192 cells; no independent frame resizing",
        "alignment_policy": "translate each cell to its rendered guide bounds; preserve guide scale and in-place pose offsets",
        "root_contract": {"anchor": [80, 132], "reference_height": 88},
        "frames": [],
    }

    for action in ACTIONS:
        output = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
        for frame_index in range(8):
            for direction_index in range(8):
                key = (action, frame_index, direction_index)
                paint_box, guide_box = measurements[key]
                tile_box = (direction_index * CELL, frame_index * CELL,
                            (direction_index + 1) * CELL, (frame_index + 1) * CELL)
                cell = painted[action].crop(tile_box)
                cropped = cell.crop(paint_box)
                scaled_size = (max(1, round(cropped.width * uniform_scale)),
                               max(1, round(cropped.height * uniform_scale)))
                scaled = cropped.resize(scaled_size, Image.Resampling.LANCZOS)

                guide_center_x = (guide_box[0] + guide_box[2]) / 2.0
                target_left = round(guide_center_x - scaled.width / 2.0)
                target_top = guide_box[3] - scaled.height
                target_right = target_left + scaled.width
                target_bottom = target_top + scaled.height
                if min(target_left, target_top) < 0 or target_right > CELL or target_bottom > CELL:
                    raise ValueError(
                        f"Normalized character clips its cell: {action}/{DIRECTIONS[direction_index]}/{frame_index} "
                        f"bounds=({target_left},{target_top},{target_right},{target_bottom})"
                    )
                cell_out = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
                cell_out.alpha_composite(scaled, (target_left, target_top))
                guide_cell = guides[action].crop(tile_box)
                allowed = np.asarray(_guide_silhouette_mask(guide_cell), dtype=np.uint8) > 0
                cell_alpha = np.asarray(cell_out.getchannel("A"), dtype=np.uint8)
                cell_out.putalpha(Image.fromarray(np.where(allowed, cell_alpha, 0).astype(np.uint8), mode="L"))
                output.alpha_composite(cell_out, (direction_index * CELL, frame_index * CELL))
                out_box = _bbox(cell_out, threshold=0)
                if not out_box:
                    raise ValueError(f"Normalized cell lost its character: {action}/{DIRECTIONS[direction_index]}/{frame_index}")
                report["frames"].append({
                    "action": action,
                    "direction": DIRECTIONS[direction_index],
                    "frame_index": frame_index,
                    "painted_input_bbox": list(paint_box),
                    "guide_bbox": list(guide_box),
                    "normalized_bbox": list(out_box),
                    "scale": round(uniform_scale, 6),
                    "translation": [target_left - paint_box[0], target_top - paint_box[1]],
                })
        normalized[action] = output
        output_dir.mkdir(parents=True, exist_ok=True)
        output.save(output_dir / f"{action.lower()}.png", format="PNG", optimize=False)
    report["source_height_median"] = statistics.median(source_heights)
    report["painted_height_median_before_normalization"] = statistics.median(painted_heights)
    report["normalized_frame_count"] = len(report["frames"])
    return normalized, report


def _to_runtime_strip(sheet: Image.Image) -> Image.Image:
    strip = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
    # Runtime strips use direction rows and frame columns.
    for frame_index in range(8):
        for direction_index in range(8):
            cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                               (direction_index + 1) * CELL, (frame_index + 1) * CELL))
            strip.alpha_composite(cell, (frame_index * CELL, direction_index * CELL))
    return strip


def _blank_strip(frame_count: int) -> Image.Image:
    return Image.new("RGBA", (CELL * frame_count, CELL * 8), (0, 0, 0, 0))


def make_definition(source_definition: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    base = copy.deepcopy(source_definition)
    base["characterId"] = candidate_id
    base["source"]["status"] = "DEV_ONLY"
    base["source"]["reference"] = "authoring/characters/factory-v3/identities/swordsman_identity_v1.json"
    base["source"]["approvedBy"] = None
    base["source"]["designLocks"] = [
        "silver-lavender-haired fantasy swordsman; bronze, gold, ivory, dark olive, and teal palette",
        "no trailing cape by default; no-cape BackAccessory slot is transparent",
        "right-hand narrow steel sword; keep the human pose and guide camera contract",
        "AI-painted coherent whole-character composite; independent equipment layers are not supplied",
        "owner visual approval required before runtime admission",
    ]
    base["tags"] = [
        "DEV_ONLY", "PLACEHOLDER", "NOT_FINAL_ART", "AI_PAINT_CANDIDATE",
        "OWNER_APPROVAL_PENDING", "FUSED_BODY_OUTFIT_HAIR_WEAPON",
    ]
    base["defaultParts"] = {
        "Body": "painted-composite",
        "Hair": "empty-hair",
        "Outfit": "empty-outfit",
        "Weapon": "empty-weapon",
        "Headgear": "empty-headgear",
        "Back": "empty-back-accessory",
    }
    for action in ACTIONS:
        base["clips"][action]["tags"] = ["INTERNAL_VISUAL_PASS", "AI_PAINT_CANDIDATE", "OWNER_APPROVAL_PENDING"]
    for action in base["clips"]:
        if action not in ACTIONS:
            base["clips"][action]["tags"] = ["PENDING_PRODUCTION", "OWNER_APPROVAL_PENDING"]
    base["parts"] = {
        "painted-composite": {
            "slot": "Body",
            "tags": ["FUSED_BODY_OUTFIT_HAIR_WEAPON", "NO_EQUIPMENT_SWAP_QA"],
            "frames": {},
        },
        **{
            part_id: {"slot": slot, "tags": ["TRANSPARENT_PLACEHOLDER_LAYER"], "frames": {}}
            for part_id, slot in EMPTY_PARTS.items()
        },
    }
    base["atlases"] = {}
    return base


def write_candidate(
    repository: Path,
    output_root: Path,
    candidate_id: str,
    source_definition_path: Path,
    normalized: dict[str, Image.Image],
) -> Path:
    if candidate_id in RETIRED_CANDIDATES:
        raise ValueError("Retired character IDs cannot be regenerated in the runtime directory")
    definition = make_definition(json.loads(source_definition_path.read_text(encoding="utf-8")), candidate_id)
    staging = output_root / "runtime-source"
    for part_id in definition["parts"]:
        for action, clip in definition["clips"].items():
            part_dir = staging / "parts" / part_id / action
            part_dir.mkdir(parents=True, exist_ok=True)
            if part_id == "painted-composite" and action in normalized:
                strip = _to_runtime_strip(normalized[action])
            else:
                strip = _blank_strip(len(clip["durations"]))
            strip.save(part_dir / "strip.png", format="PNG", optimize=False)
    definition_path = staging / "sprite-definition.json"
    definition_path.parent.mkdir(parents=True, exist_ok=True)
    definition_path.write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    packer = repository / "tools" / "pack-modular-sprites.py"
    subprocess.run(
        [sys.executable, str(packer), "--definition", str(definition_path), "--sources", str(staging),
         "--repository", str(repository), "--deduplicate"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return repository / "assets" / "characters" / candidate_id / "sprite.json"


def _write_gifs(
    sheets: dict[str, Image.Image],
    source_definition_path: Path,
    evidence_dir: Path,
    repository: Path,
) -> dict[str, str]:
    definition = json.loads(source_definition_path.read_text(encoding="utf-8"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for action, sheet in sheets.items():
        frames: list[Image.Image] = []
        durations = definition["clips"][action]["durations"]
        for frame_index in range(len(durations)):
            line = Image.new("RGBA", (SHEET, CELL), (24, 34, 43, 255))
            for direction_index in range(8):
                cell = sheet.crop((direction_index * CELL, frame_index * CELL,
                                   (direction_index + 1) * CELL, (frame_index + 1) * CELL))
                line.alpha_composite(cell, (direction_index * CELL, 0))
            frames.append(line.convert("RGB"))
        frame_durations = list(map(int, durations))
        if action == "BasicAttack":
            frames.append(frames[-1].copy())
            frame_durations[-1] += 700
            frame_durations.append(700)
        gif_path = evidence_dir / f"v3-ai-painted-{action.lower()}-8-directions.gif"
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=frame_durations,
                       loop=0, optimize=False, disposal=2)
        outputs[action] = gif_path.relative_to(repository).as_posix()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--source-definition", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--master-prompt", type=Path, required=True)
    for action in ACTIONS:
        parser.add_argument(f"--{action.lower()}-prompt", type=Path, required=True)
    parser.add_argument("--alpha-threshold", type=int, default=ALPHA_THRESHOLD)
    parser.add_argument("--all-prompts-exact", action="store_true",
                        help="Record every supplied action prompt as the exact request used for this generation")
    parser.add_argument("--generation-label", default="existing selection; see source job record")
    for action in ACTIONS:
        parser.add_argument(f"--{action.lower()}-image", type=Path, required=True)
        parser.add_argument(f"--{action.lower()}-guide", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()
    output_root = args.output_root.resolve()
    source_definition_path = (repository / args.source_definition).resolve() if not args.source_definition.is_absolute() else args.source_definition.resolve()
    painted_paths = {action: getattr(args, f"{action.lower()}_image").resolve() for action in ACTIONS}
    guide_paths = {action: getattr(args, f"{action.lower()}_guide").resolve() for action in ACTIONS}
    prompt_paths = {action: getattr(args, f"{action.lower()}_prompt").resolve() for action in ACTIONS}
    master_prompt_path = args.master_prompt.resolve()
    for path in [master_prompt_path, *prompt_paths.values(), *painted_paths.values(), *guide_paths.values()]:
        try:
            path.relative_to(repository)
        except ValueError as exc:
            raise ValueError(f"Job input must be stored inside the repository for reproducibility: {path}") from exc
    sheet_dir = output_root / "sheets"
    normalized, report = prepare_painted_sheets(
        painted_paths, guide_paths, sheet_dir, alpha_threshold=args.alpha_threshold,
    )
    runtime_definition = write_candidate(repository, output_root, args.candidate_id, source_definition_path, normalized)
    gifs = _write_gifs(normalized, source_definition_path, (repository / args.evidence_dir).resolve(), repository)
    job = {
        "schema_version": 1,
        "character_id": "swordsman_male_v3",
        "candidate_character_id": args.candidate_id,
        "provider": "OpenAI ImageGen",
        "status": "AI_PAINT_CANDIDATE_OWNER_APPROVAL_PENDING",
        "source_definition": str(source_definition_path.relative_to(repository)),
        "identity_reference": {
            "file": "authoring/characters/gait-rig-v50/approved-warrior-seed.png",
            "sha256": json.loads((repository / "authoring/characters/factory-v3/identities/swordsman_identity_v1.json").read_text(encoding="utf-8"))["reference_sha256"],
        },
        "master_prompt": {"file": str(master_prompt_path.relative_to(repository)), "sha256": sha256(master_prompt_path)},
        "action_prompts": {
            action: {
                "file": str(prompt_paths[action].relative_to(repository)),
                "sha256": sha256(prompt_paths[action]),
                "fidelity": "EXACT_REQUEST" if args.all_prompts_exact or action == "BasicAttack" else "CANONICAL_RECONSTRUCTION_ORIGINAL_TEXT_NOT_RETAINED",
            }
            for action in ACTIONS
        },
        "selected_generation": {
            "generation_label": args.generation_label,
            "selection_status": "PENDING_VISUAL_REVIEW",
            "background_cleanup": "alpha below 128 removed and remaining alpha remapped linearly; RGB color decontamination not applied",
        },
        "painted_inputs": {
            action: {"file": str(painted_paths[action].relative_to(repository)), "sha256": sha256(painted_paths[action])}
            for action in ACTIONS
        },
        "guide_inputs": {
            action: {"file": str(guide_paths[action].relative_to(repository)), "sha256": sha256(guide_paths[action])}
            for action in ACTIONS
        },
        "source_motion_license": "Mesh2Motion CC0 1.0; only raster sprite guides were used as image references, not source motion files.",
        "output_license_note": "Generated output is subject to the image provider's applicable terms; no separate CC0 claim is made for painted pixels.",
        "normalization": report,
        "runtime_definition": str(runtime_definition.relative_to(repository)),
        "review_gifs": gifs,
        "modularity": {
            "status": "PARTIAL_FUSED_COMPOSITE",
            "composite_contains": ["BaseBody", "Hair", "Outfit", "Weapon"],
            "separate_layers": [],
            "back_accessory_default": "transparent",
            "owner_approval": False,
        },
    }
    (output_root / "job.json").write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")
    validator = repository / "tools" / "character_factory_v3" / "validate_runtime_package.cjs"
    result = subprocess.run(["node", str(validator), str(runtime_definition)], cwd=repository, capture_output=True, text=True)
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError("Painted runtime candidate failed schema/atlas validation")
    print(json.dumps({"passed": True, "runtime": str(runtime_definition.relative_to(repository)), "validation": json.loads(result.stdout), "job": str((output_root / "job.json").relative_to(repository))}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Painted sheet import failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
