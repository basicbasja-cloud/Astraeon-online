"""Render-contract and frame-continuity checks tailored to V3 guide sets."""
from __future__ import annotations

import json
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from PIL import Image

from contracts import DIRECTIONS, sha256_file

REQUIRED_PASSES = ("rgb", "silhouette", "depth", "normal", "body_segmentation", "weapon_mask")
DIRECTION_YAWS = {"S": 0, "SW": -45, "W": -90, "NW": -135, "N": -180, "NE": -225, "E": -270, "SE": 45}


def validate_guide_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    root = manifest_path.parent
    if manifest.get("width") != 320 or manifest.get("height") != 320:
        errors.append("Guide dimensions must be 320x320")
    if manifest.get("directions") != list(DIRECTIONS):
        errors.append("Guide direction order must be the canonical unmirrored order")
    if manifest.get("pose_kind") != "REST_ONLY_NONPRODUCTION":
        errors.append("This review validator expects a rest-pose rig smoke render, not a production clip")
    if manifest.get("mirroring") != "none":
        errors.append("Eight-direction guides must use real camera turns and no mirroring")
    if manifest.get("root_pixel") != [160, 264]:
        errors.append("Static rig smoke must retain the V2 root pixel")
    frames = manifest.get("frames", [])
    if len(frames) != 8:
        errors.append(f"Expected one frame in each direction; found {len(frames)} records")
    seen: list[str] = []
    for frame in frames:
        direction = frame.get("direction")
        seen.append(direction)
        if frame.get("yaw_degrees") != DIRECTION_YAWS.get(direction):
            errors.append(f"Unexpected yaw for {direction}: {frame.get('yaw_degrees')}")
        if frame.get("frame_index") != 0:
            errors.append(f"Rest-pose frame index must be 0 for {direction}")
        if frame.get("visible_alpha_pixels", 0) <= 0:
            errors.append(f"No visible character pixels in {direction}")
        if 4 not in frame.get("object_index_values", []):
            errors.append(f"Weapon segmentation is missing in {direction}")
        passes = frame.get("passes", {})
        missing = [name for name in REQUIRED_PASSES if name not in passes]
        if missing:
            errors.append(f"{direction} is missing passes: {', '.join(missing)}")
        for name, entry in passes.items():
            raw_path = PurePosixPath(entry.get("file", ""))
            if raw_path.is_absolute() or ".." in raw_path.parts:
                errors.append(f"Unsafe pass path for {direction}/{name}: {raw_path}")
                continue
            path = root.joinpath(*raw_path.parts)
            if not path.resolve().is_relative_to(root.resolve()):
                errors.append(f"Pass path escapes the guide directory through a symlink: {raw_path}")
                continue
            if not path.is_file():
                errors.append(f"Missing {name} pass for {direction}: {path}")
                continue
            if sha256_file(path) != entry.get("sha256"):
                errors.append(f"Digest mismatch for {name} pass in {direction}")
            try:
                with Image.open(path) as image:
                    if image.size != (320, 320):
                        errors.append(f"{name} pass for {direction} is not 320x320")
                    if image.mode != "RGBA":
                        errors.append(f"{name} pass for {direction} is not RGBA")
                    image.load()
                    if name == "rgb":
                        alpha = image.getchannel("A")
                        if alpha.getbbox() is None:
                            errors.append(f"RGB pass for {direction} is fully transparent")
                        if alpha.getpixel((0, 0)) != 0:
                            errors.append(f"RGB pass for {direction} has opaque background at the canvas corner")
                    if name in ("silhouette", "weapon_mask", "body_segmentation") and image.getchannel("A").getbbox() is None:
                        errors.append(f"{name} pass for {direction} has no pixels")
            except Exception as exc:  # Pillow reports the specific decode failure.
                errors.append(f"Cannot decode {name} pass for {direction}: {exc}")
        if "rgb" in passes and "silhouette" in passes:
            try:
                rgb_rel = PurePosixPath(passes["rgb"].get("file", ""))
                silhouette_rel = PurePosixPath(passes["silhouette"].get("file", ""))
                if any(path.is_absolute() or ".." in path.parts for path in (rgb_rel, silhouette_rel)):
                    raise ValueError("Unsafe RGB or silhouette path")
                rgb_path = root.joinpath(*rgb_rel.parts)
                silhouette_path = root.joinpath(*silhouette_rel.parts)
                with Image.open(rgb_path) as rgb_image, Image.open(silhouette_path) as silhouette_image:
                    rgb_alpha = rgb_image.convert("RGBA").getchannel("A")
                    silhouette_alpha = silhouette_image.convert("RGBA").getchannel("A")
                    if rgb_alpha.tobytes() != silhouette_alpha.tobytes():
                        errors.append(f"Silhouette alpha is not registered to the RGB render in {direction}")
            except Exception as exc:
                errors.append(f"Cannot compare RGB and silhouette alpha in {direction}: {exc}")
    if seen != list(DIRECTIONS):
        errors.append("Frame records are missing, duplicated, or out of direction order")
    return {
        "passed": not errors,
        "gate_scope": "static rig/camera/pass smoke only; not an animation or art approval",
        "errors": errors,
        "direction_count": len(frames),
        "passes_per_direction": list(REQUIRED_PASSES),
    }


def validate_production_guide_manifest(manifest_path: Path, required_actions: list[str]) -> dict[str, Any]:
    """Validate a sampled animation guide package across every required direction."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    root = manifest_path.parent
    if manifest.get("pose_kind") != "PRODUCTION_ANIMATION":
        errors.append("Paint handoff requires rendered production animation guides")
    if (manifest.get("width"), manifest.get("height")) != (320, 320):
        errors.append("Production guide dimensions must be 320x320")
    if manifest.get("directions") != list(DIRECTIONS) or manifest.get("mirroring") != "none":
        errors.append("Production guides must cover the canonical unmirrored directions")
    if manifest.get("root_pixel") != [160, 264]:
        errors.append("Production guides must retain the V2 root pixel")
    if manifest.get("status") != "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING":
        errors.append("Production guide manifest must retain its internal candidate status")
    actions = manifest.get("actions", {})
    for action in required_actions:
        if action not in actions:
            errors.append(f"Required production action is missing: {action}")
    frame_records = manifest.get("frames", [])
    action_names = list(actions)
    expected = set()
    for action in action_names:
        action_record = actions[action]
        frame_count = int(action_record.get("frame_count", 0))
        if frame_count <= 0:
            errors.append(f"Action {action} has an invalid frame_count")
            continue
        durations = action_record.get("durations", [])
        if len(durations) != frame_count or any(not isinstance(value, (int, float)) or value <= 0 for value in durations):
            errors.append(f"Action {action} must have one positive duration per sampled frame")
        if not isinstance(action_record.get("loop"), bool):
            errors.append(f"Action {action} is missing an explicit loop policy")
        provenance = action_record.get("motion_provenance", {})
        for field in ("id", "source_url", "source_format", "file_sha256", "license_evidence", "production_status"):
            if field not in provenance:
                errors.append(f"Action {action} motion provenance is missing {field}")
        digest = provenance.get("file_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
            errors.append(f"Action {action} motion provenance has an invalid source hash")
        if provenance.get("production_status") not in ("CANDIDATE", "APPROVED_FOR_PRODUCTION"):
            errors.append(f"Action {action} motion provenance is not an eligible reviewed candidate")
        if not isinstance(provenance.get("license_evidence"), list) or not provenance.get("license_evidence"):
            errors.append(f"Action {action} motion provenance has no license evidence")
        for evidence in provenance.get("license_evidence", []):
            evidence_path = Path(evidence)
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                errors.append(f"Action {action} has an unsafe license evidence path")
            elif not (Path(__file__).resolve().parents[2] / evidence_path).is_file():
                errors.append(f"Action {action} license evidence file is missing: {evidence}")
        events = action_record.get("events", [])
        total_duration = sum(value for value in durations if isinstance(value, (int, float)))
        for event in events:
            phase = event.get("phase")
            time_ms = event.get("time_ms")
            frame_index = event.get("frame_index")
            if not isinstance(phase, (int, float)) or not 0 <= phase <= 1:
                errors.append(f"Action {action} semantic event has an invalid phase")
            if not isinstance(time_ms, (int, float)) or not 0 <= time_ms <= total_duration:
                errors.append(f"Action {action} semantic event has an invalid time")
            if not isinstance(frame_index, int) or not 0 <= frame_index < frame_count:
                errors.append(f"Action {action} semantic event has an invalid frame index")
        for frame_index in range(frame_count):
            for direction in DIRECTIONS:
                expected.add((action, frame_index, direction))
    observed = set()
    for frame in frame_records:
        action = frame.get("action")
        direction = frame.get("direction")
        key = (action, frame.get("frame_index"), direction)
        if key in observed:
            errors.append(f"Duplicate production guide frame: {key}")
        observed.add(key)
        if direction not in DIRECTIONS:
            errors.append(f"Unknown production guide direction: {direction}")
        if not isinstance(frame.get("duration_ms"), (int, float)) or frame.get("duration_ms", 0) <= 0:
            errors.append(f"Frame has no positive explicit duration: {key}")
        if not isinstance(frame.get("source_frame"), (int, float)):
            errors.append(f"Frame has no source-frame reference: {key}")
        sockets = frame.get("sockets", {})
        for socket in ("root", "head", "hand_R", "hand_L", "back", "waist"):
            point = sockets.get(socket)
            if not isinstance(point, list) or len(point) != 2 or any(not isinstance(value, (int, float)) or not 0 <= value <= 320 for value in point):
                errors.append(f"Frame has an invalid {socket} socket: {key}")
        action_record = actions.get(action, {})
        durations = action_record.get("durations", [])
        if isinstance(frame.get("frame_index"), int) and 0 <= frame["frame_index"] < len(durations):
            if frame.get("duration_ms") != durations[frame["frame_index"]]:
                errors.append(f"Frame duration differs from the shared action timeline: {key}")
        passes = frame.get("passes", {})
        missing = [name for name in REQUIRED_PASSES if name not in passes]
        if missing:
            errors.append(f"{key} is missing passes: {', '.join(missing)}")
        for name, entry in passes.items():
            relative = PurePosixPath(entry.get("file", ""))
            if relative.is_absolute() or ".." in relative.parts:
                errors.append(f"Unsafe production pass path for {key}/{name}")
                continue
            path = root.joinpath(*relative.parts)
            if not path.resolve().is_relative_to(root.resolve()):
                errors.append(f"Production pass path escapes through a symlink: {relative}")
                continue
            if not path.is_file():
                errors.append(f"Missing production pass for {key}/{name}: {path}")
                continue
            if sha256_file(path) != entry.get("sha256"):
                errors.append(f"Digest mismatch for production pass {key}/{name}")
            try:
                with Image.open(path) as image:
                    if image.size != (320, 320) or image.mode != "RGBA":
                        errors.append(f"Production pass {key}/{name} must be RGBA 320x320")
                    image.load()
            except Exception as exc:
                errors.append(f"Cannot decode production pass {key}/{name}: {exc}")
    missing_frames = sorted(expected - observed)
    extra_frames = sorted(observed - expected)
    if missing_frames:
        errors.append(f"Production guide coverage is incomplete; missing {len(missing_frames)} action/frame/direction records")
    if extra_frames:
        errors.append(f"Production guide manifest has {len(extra_frames)} unexpected action/frame/direction records")
    return {
        "passed": not errors,
        "gate_scope": "sampled production guide structure and pass files; visual motion acceptance remains a human gate",
        "errors": errors,
        "required_actions": required_actions,
        "action_count": len(actions),
        "frame_record_count": len(frame_records),
        "expected_frame_record_count": len(expected),
    }


def silhouette_continuity(frame_paths: list[Path], alpha_threshold: int = 10) -> dict[str, Any]:
    """Compute adjacent-frame silhouette IoU; this is a review signal, not a quality verdict."""
    if len(frame_paths) < 2:
        return {"passed": False, "error": "At least two frames are required", "pairs": []}
    masks: list[set[int]] = []
    for path in frame_paths:
        with Image.open(path) as image:
            image = image.convert("RGBA")
            if image.size != (320, 320):
                return {"passed": False, "error": f"Unexpected frame size in {path}", "pairs": []}
            alpha = image.getchannel("A")
            mask = {index for index, value in enumerate(alpha.getdata()) if value > alpha_threshold}
            if not mask:
                return {"passed": False, "error": f"Empty silhouette in {path}", "pairs": []}
            masks.append(mask)
    pairs = []
    scores = []
    for index, (left, right) in enumerate(zip(masks, masks[1:])):
        union = len(left | right)
        score = len(left & right) / union if union else 1.0
        scores.append(score)
        pairs.append({"from": frame_paths[index].name, "to": frame_paths[index + 1].name, "iou": round(score, 6)})
    return {
        "passed": True,
        "signal_only": True,
        "threshold": alpha_threshold,
        "mean_iou": round(sum(scores) / len(scores), 6),
        "min_iou": round(min(scores), 6),
        "pairs": pairs,
        "interpretation": "Large adjacent silhouette changes need human review; action phases can legitimately change silhouette.",
    }


def make_direction_contact_sheet(manifest_path: Path, output_path: Path, scale: float = 1) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    tile_w, tile_h = int(320 * scale), int(320 * scale)
    sheet = Image.new("RGBA", (tile_w * 4, (tile_h + 24) * 2), (32, 36, 48, 255))
    from PIL import ImageDraw

    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(manifest["frames"]):
        x = (index % 4) * tile_w
        y = (index // 4) * (tile_h + 24)
        image_path = root / frame["passes"]["rgb"]["file"]
        with Image.open(image_path) as image:
            tile = image.convert("RGBA")
            if scale != 1:
                resample = Image.Resampling.LANCZOS if scale < 1 else Image.Resampling.NEAREST
                tile = tile.resize((tile_w, tile_h), resample)
            sheet.alpha_composite(tile, (x, y))
        draw.text((x + 6, y + tile_h + 4), frame["direction"], fill=(255, 238, 185, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=False)


def make_motion_contact_sheet(manifest_path: Path, action: str, output_path: Path, scale: float = 0.5) -> None:
    """Create an eight-direction by sampled-frame review sheet for one action."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = sorted((frame for frame in manifest.get("frames", []) if frame.get("action") == action), key=lambda item: (item["frame_index"], DIRECTIONS.index(item["direction"])))
    frame_count = manifest.get("actions", {}).get(action, {}).get("frame_count", 0)
    if len(rows) != frame_count * len(DIRECTIONS):
        raise ValueError(f"Cannot make a complete contact sheet for {action}: {len(rows)} rendered frames")
    tile_w = int(manifest["width"] * scale)
    tile_h = int(manifest["height"] * scale)
    label_h = 20
    sheet = Image.new("RGBA", (tile_w * len(DIRECTIONS), (tile_h + label_h) * frame_count), (30, 34, 46, 255))
    from PIL import ImageDraw

    draw = ImageDraw.Draw(sheet)
    for frame in rows:
        col = DIRECTIONS.index(frame["direction"])
        row = frame["frame_index"]
        x, y = col * tile_w, row * (tile_h + label_h)
        relative = PurePosixPath(frame["passes"]["rgb"]["file"])
        image_path = manifest_path.parent.joinpath(*relative.parts)
        with Image.open(image_path) as image:
            tile = image.convert("RGBA")
            if scale != 1:
                tile = tile.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            sheet.alpha_composite(tile, (x, y))
        draw.text((x + 5, y + tile_h + 3), f"{row:02d} {frame['direction']}", fill=(255, 238, 190, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=False)
