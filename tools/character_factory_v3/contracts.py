"""Config, provenance, and content-addressing contracts for Factory V3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

DIRECTIONS = ("S", "SW", "W", "NW", "N", "NE", "E", "SE")
REQUIRED_ACTIONS = ("Idle", "Walk", "BasicAttack")
MOTION_STATUSES = {
    "CANDIDATE",
    "APPROVED_FOR_PRODUCTION",
    "RESEARCH_ONLY",
    "BLOCKED_LICENSE_UNKNOWN",
    "BLOCKED_ACCESS_REQUIRED",
    "REJECTED_VISUAL_QUALITY",
    "REJECTED_RETARGET_QUALITY",
}
PROVENANCE_FIELDS = (
    "id",
    "provider",
    "source_title",
    "source_url",
    "acquisition_date",
    "original_filename",
    "file_sha256",
    "original_skeleton",
    "source_format",
    "original_fps",
    "duration_seconds",
    "loop",
    "license_summary",
    "commercial_use_status",
    "retarget_permission_status",
    "modification_status",
    "production_status",
    "local_path",
    "license_evidence",
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def repo_path(root: Path, raw: str) -> Path:
    relative = PurePosixPath(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Repository paths must be relative and cannot traverse parents: {raw}")
    candidate = root.joinpath(*relative.parts)
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Repository paths cannot escape through symlinks: {raw}")
    return candidate


def validate_rig_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bones = spec.get("bones")
    if not isinstance(bones, list) or len(bones) != spec.get("validation", {}).get("expected_bone_count"):
        errors.append("Rig bone list does not match the expected bone count")
        bones = bones if isinstance(bones, list) else []
    if len(bones) != len(set(bones)):
        errors.append("Rig bone names are not unique")
    bone_set = set(bones)
    if spec.get("root") not in bone_set:
        errors.append("Canonical root bone is missing")
    coordinates = spec.get("coordinate_system", {})
    if coordinates.get("up_axis") != "Z" or coordinates.get("forward_axis") != "-Y":
        errors.append("Canonical rig must remain Z-up and -Y-forward")
    scale = coordinates.get("source_height_blender_units")
    if not isinstance(scale, (int, float)) or scale <= 0:
        errors.append("Canonical rig source scale must be a positive height")
    if spec.get("reuse_scope", {}).get("shared_skeleton_not_shared_mesh") is not True:
        errors.append("Canonical rig reuse must separate the shared skeleton from class-specific meshes")
    for chain in spec.get("validation", {}).get("required_chains", []):
        missing = [name for name in chain if name not in bone_set]
        if missing:
            errors.append("Missing required rig chain bones: " + ", ".join(missing))
    anchors = spec.get("anchor_bones", {})
    for socket, bone in anchors.items():
        if bone not in bone_set:
            errors.append(f"Anchor {socket} refers to missing bone {bone}")
    if spec.get("render_contract", {}).get("direction_order") != list(DIRECTIONS):
        errors.append("Rig direction order differs from the V2 camera contract")
    if spec.get("render_contract", {}).get("mirroring") != "none":
        errors.append("Canonical rig must not mirror directions")
    return errors


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not config.get("id"):
        errors.append("Character config is missing id")
    if config.get("class_id") != "Swordsman":
        errors.append("The first V3 vertical slice must use the Swordsman class")
    if config.get("status") != "DEV_ONLY":
        errors.append("The V3 first character must remain DEV_ONLY until approved")
    render = config.get("render", {})
    if (render.get("width"), render.get("height"), render.get("root")) != (320, 320, [160, 264]):
        errors.append("Render contract must stay at 320x320 with root (160,264)")
    if render.get("directions") != list(DIRECTIONS):
        errors.append("Direction order must be S, SW, W, NW, N, NE, E, SE")
    if set(config.get("required_actions", [])) != set(REQUIRED_ACTIONS):
        errors.append("Required vertical slice actions must be Idle, Walk, and BasicAttack")
    if config.get("paint", {}).get("layers") != ["BaseBody", "Hair", "Outfit", "Weapon", "Headgear", "BackAccessory"]:
        errors.append("Logical runtime layers differ from the V2 six-layer contract")
    if config.get("output", {}).get("runtime_admitted") is not False:
        errors.append("A V3 candidate cannot be runtime-admitted before review")
    return errors


def validate_motion_record(record: dict[str, Any]) -> list[str]:
    errors = [f"Missing required provenance field: {field}" for field in PROVENANCE_FIELDS if field not in record]
    status = record.get("production_status")
    if status not in MOTION_STATUSES:
        errors.append(f"Invalid production status: {status}")
    if status in ("CANDIDATE", "APPROVED_FOR_PRODUCTION"):
        for field in (
            "acquisition_date", "original_filename", "file_sha256", "original_skeleton",
            "source_format", "original_fps", "duration_seconds", "loop", "local_path",
        ):
            if record.get(field) in (None, "", []):
                errors.append(f"Motion is missing {field}")
        if record.get("source_format") not in ("BVH", "FBX", "BLEND", "GLB", "GLTF", "AMC", "ASF"):
            errors.append("Motion has an unsupported source_format")
        if not isinstance(record.get("original_fps"), (int, float)) or record.get("original_fps", 0) <= 0:
            errors.append("Motion has an invalid original_fps")
        if not isinstance(record.get("duration_seconds"), (int, float)) or record.get("duration_seconds", 0) <= 0:
            errors.append("Motion has an invalid duration_seconds")
        if not isinstance(record.get("loop"), bool):
            errors.append("Motion must declare a loop boolean")
        if not isinstance(record.get("license_evidence"), list) or not record.get("license_evidence"):
            errors.append("Motion is missing retained license evidence")
        digest = record.get("file_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            errors.append("Motion has an invalid SHA-256")
        archive_digest = record.get("source_archive_sha256")
        if archive_digest is not None and (
            not isinstance(archive_digest, str) or len(archive_digest) != 64
            or any(c not in "0123456789abcdef" for c in archive_digest.lower())
        ):
            errors.append("Motion has an invalid source archive SHA-256")
        if not isinstance(record.get("license_summary"), str) or not record.get("license_summary", "").strip():
            errors.append("Motion is missing a license summary")
        if record.get("commercial_use_status") not in ("APPROVED", "APPROVED_WITH_LIMITS"):
            errors.append("Motion lacks a reviewed commercial-use status")
        if record.get("retarget_permission_status") != "APPROVED":
            errors.append("Motion lacks reviewed retarget permission")
    return errors


def motion_gate(config: dict[str, Any], registry: dict[str, Any], repo_root: Path | None = None) -> dict[str, Any]:
    imported = {record.get("id"): record for record in registry.get("imported_motions", [])}
    blocked: list[dict[str, Any]] = []
    for action in config.get("required_actions", []):
        motion_id = config.get("actions", {}).get(action, {}).get("motion_id")
        record = imported.get(motion_id)
        if record is None:
            blocked.append({"action": action, "motion_id": motion_id, "reason": "no imported motion record"})
            continue
        issues = validate_motion_record(record)
        if repo_root is not None and record.get("production_status") == "APPROVED_FOR_PRODUCTION":
            try:
                motion_path = repo_path(repo_root, record.get("local_path", ""))
                if not motion_path.is_file():
                    issues.append(f"Approved motion file is missing: {record.get('local_path')}")
                elif sha256_file(motion_path) != record.get("file_sha256"):
                    issues.append(f"Approved motion file hash does not match provenance: {record.get('local_path')}")
                evidence = record.get("license_evidence", [])
                for path in evidence:
                    evidence_path = repo_path(repo_root, path)
                    if not evidence_path.is_file():
                        issues.append(f"License evidence file is missing: {path}")
            except ValueError as exc:
                issues.append(str(exc))
        if issues:
            blocked.append({"action": action, "motion_id": motion_id, "reason": "invalid provenance", "issues": issues})
        elif record.get("production_status") != "APPROVED_FOR_PRODUCTION":
            blocked.append({"action": action, "motion_id": motion_id, "reason": record.get("production_status")})
    return {
        "passed": not blocked,
        "required_actions": list(config.get("required_actions", [])),
        "blocked": blocked,
        "old_v2_motion_fallback": False,
    }


def cache_key(
    *,
    source_hashes: dict[str, str],
    rig_hash: str,
    motion_hash: str,
    retarget: dict[str, Any],
    cleanup: dict[str, Any],
    stylization: dict[str, Any],
    camera: dict[str, Any],
    prop_hash: str,
    sampler: dict[str, Any],
    script_hashes: dict[str, str],
) -> str:
    """Return one deterministic build key. Missing inputs must use an explicit marker."""
    return canonical_digest({
        "source_hashes": source_hashes,
        "rig_hash": rig_hash,
        "motion_hash": motion_hash,
        "retarget": retarget,
        "cleanup": cleanup,
        "stylization": stylization,
        "camera": camera,
        "prop_hash": prop_hash,
        "sampler": sampler,
        "script_hashes": script_hashes,
    })
