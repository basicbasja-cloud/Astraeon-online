#!/usr/bin/env python3
"""Config-driven command line entry point for Astraeon Character Factory V3."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from contracts import (
    DIRECTIONS,
    cache_key,
    motion_gate,
    read_json,
    sha256_file,
    validate_config,
    validate_rig_spec,
    write_json,
)
from paint_provider import ManualHandoffProvider
from qa import make_direction_contact_sheet, validate_guide_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = REPO_ROOT / "authoring/characters/factory-v3"
TOOL_ROOT = Path(__file__).resolve().parent
BLENDER_ROOT = TOOL_ROOT / "blender"


def load_character(character_id: str) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    config_path = FACTORY_ROOT / "configs" / f"{character_id}.json"
    config = read_json(config_path)
    if config.get("id") != character_id:
        raise ValueError(f"Config ID mismatch for {config_path}")
    rig_spec = read_json(REPO_ROOT / config["rig"]["spec"])
    identity = read_json(REPO_ROOT / config["identity"])
    registry = read_json(REPO_ROOT / config["motion_registry"])
    return config_path, config, rig_spec, {"identity": identity, "registry": registry}


def check_preflight(character_id: str) -> dict[str, Any]:
    config_path, config, rig_spec, other = load_character(character_id)
    errors = validate_config(config) + validate_rig_spec(rig_spec)
    source_path = REPO_ROOT / config["rig"]["source_scene"]
    source_hash = sha256_file(source_path) if source_path.is_file() else None
    expected_source_hash = rig_spec.get("source_scene_sha256")
    if source_hash != expected_source_hash:
        errors.append(f"Source scene digest mismatch: expected {expected_source_hash}, got {source_hash}")
    identity_path = REPO_ROOT / config["identity"]
    identity_hash = sha256_file(identity_path) if identity_path.is_file() else None
    if identity_hash != other["identity"].get("file_sha256"):
        ref_path = REPO_ROOT / other["identity"]["reference"]
        ref_hash = sha256_file(ref_path) if ref_path.is_file() else None
        if ref_hash != other["identity"].get("reference_sha256"):
            errors.append("Identity reference hash does not match its V2 approved seed lock")
    motion = motion_gate(config, other["registry"], REPO_ROOT)
    candidate_states = [
        {"id": item.get("id"), "provider": item.get("provider"), "status": item.get("production_status")}
        for item in other["registry"].get("candidates", [])
    ]
    return {
        "passed": not errors,
        "character_id": character_id,
        "config": str(config_path.relative_to(REPO_ROOT)),
        "rig_spec_errors": validate_rig_spec(rig_spec),
        "errors": errors,
        "source_scene_sha256": source_hash,
        "identity_reference_sha256": other["identity"].get("reference_sha256"),
        "motion_gate": motion,
        "motion_candidates": candidate_states,
        "legacy_v2_motion_fallback": False,
    }


def blender_version(blender: str) -> tuple[tuple[int, int, int], str]:
    result = subprocess.run([blender, "--version"], check=True, capture_output=True, text=True)
    match = re.search(r"Blender\s+(\d+)\.(\d+)\.(\d+)", result.stdout)
    if not match:
        raise RuntimeError(f"Could not parse Blender version from: {result.stdout[:300]}")
    version = tuple(map(int, match.groups()))
    return version, match.group(0)


def blender_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("ALSOFT_DRIVERS", "null")
    env.setdefault("SDL_AUDIODRIVER", "dummy")
    env.setdefault("BLENDER_USER_CONFIG", "/tmp/blender-user-config")
    env.setdefault("XDG_CACHE_HOME", "/tmp/blender-cache")
    env.setdefault("MESA_SHADER_CACHE_DIR", "/tmp/blender-cache/mesa")
    return env


def invoke_blender(blender: str, script: Path, args: list[str]) -> str:
    command = [blender, "--background", "--python", str(script), "--", *args]
    result = subprocess.run(command, cwd=REPO_ROOT, env=blender_env(), capture_output=True, text=True)
    output = result.stdout + result.stderr
    # Blender 5.x may log a Python traceback but still exit with status 0.
    if result.returncode or "Traceback (most recent call last)" in output:
        raise RuntimeError(f"Blender stage failed ({result.returncode}):\n{output[-10000:]}")
    return output


def build_rig(character_id: str, blender: str, force: bool = False) -> dict[str, Any]:
    _, config, rig_spec, _ = load_character(character_id)
    version, version_text = blender_version(blender)
    required_version = tuple(map(int, rig_spec["blender_min_version"].split(".")[:3]))
    if version < required_version:
        raise RuntimeError(f"Blender {rig_spec['blender_min_version']} or newer is required; found {version_text}")
    source_path = REPO_ROOT / config["rig"]["source_scene"]
    output_path = REPO_ROOT / config["rig"]["scene"]
    manifest_path = FACTORY_ROOT / "manifests" / "astraeon_humanoid_male_v1.rig.json"
    script = BLENDER_ROOT / "strip_legacy_actions.py"
    rig_spec_path = REPO_ROOT / config["rig"]["spec"]
    rig_spec_hash = sha256_file(rig_spec_path)
    script_hash = sha256_file(script)
    if output_path.is_file() and manifest_path.is_file() and not force:
        old = read_json(manifest_path)
        if (
            old.get("source_scene_sha256") == rig_spec["source_scene_sha256"]
            and old.get("rig_spec_sha256") == rig_spec_hash
            and old.get("strip_script_sha256") == script_hash
            and old.get("output_scene_sha256") == sha256_file(output_path)
        ):
            if old.get("remaining_action_count") == 0 and old.get("bones") == rig_spec["bones"]:
                return {"passed": True, "cached": True, "scene": str(output_path.relative_to(REPO_ROOT)), "manifest": str(manifest_path.relative_to(REPO_ROOT)), "blender": version_text}
    output = invoke_blender(blender, script, [
        "--source", str(source_path),
        "--output", str(output_path),
        "--manifest", str(manifest_path),
        "--expected-source-sha256", rig_spec["source_scene_sha256"],
        "--rig-spec-sha256", rig_spec_hash,
        "--strip-script-sha256", script_hash,
        "--expected-armature", rig_spec["skeleton_object"],
        "--expected-bones", json.dumps(rig_spec["bones"], separators=(",", ":")),
    ])
    manifest = read_json(manifest_path)
    passed = (
        manifest.get("bone_count") == rig_spec["validation"]["expected_bone_count"]
        and manifest.get("bones") == rig_spec["bones"]
        and manifest.get("remaining_action_count") == 0
        and manifest.get("output_scene_sha256") == sha256_file(output_path)
    )
    if not passed:
        raise RuntimeError("Generated V3 rig failed its action-free manifest checks")
    return {"passed": True, "cached": False, "scene": str(output_path.relative_to(REPO_ROOT)), "manifest": str(manifest_path.relative_to(REPO_ROOT)), "blender": version_text, "log": output[-2000:]}


def render_rig_review(character_id: str, blender: str, force: bool = False) -> dict[str, Any]:
    _, config, rig_spec, _ = load_character(character_id)
    scene_path = REPO_ROOT / config["rig"]["scene"]
    if not scene_path.is_file():
        build_rig(character_id, blender)
    renderer = BLENDER_ROOT / "render_guides.py"
    cache_seed = cache_key(
        source_hashes={
            "rig_scene": sha256_file(scene_path),
            "character_config": sha256_file(FACTORY_ROOT / "configs" / f"{character_id}.json"),
            "rig_spec": sha256_file(REPO_ROOT / config["rig"]["spec"]),
        },
        rig_hash=sha256_file(scene_path),
        motion_hash="NONE_STATIC_REST_SMOKE",
        retarget={},
        cleanup={},
        stylization={},
        camera=rig_spec["render_contract"],
        prop_hash="SOURCE_SCENE_PROPS",
        sampler={"pose_kind": "REST_ONLY_NONPRODUCTION"},
        script_hashes={
            "render_guides.py": sha256_file(renderer),
            "qa.py": sha256_file(TOOL_ROOT / "qa.py"),
            "contracts.py": sha256_file(TOOL_ROOT / "contracts.py"),
            "run.py": sha256_file(TOOL_ROOT / "run.py"),
        },
    )[:12]
    output = FACTORY_ROOT / "review" / f"rig-smoke-{cache_seed}"
    manifest_path = output / "manifest.json"
    qa_path = output / "qa.json"
    if manifest_path.is_file() and qa_path.is_file() and not force:
        existing = read_json(qa_path)
        full_sheet = output / existing.get("review_contact_sheet", "contact-sheet.png")
        game_sheet = output / existing.get("game_scale_contact_sheet", "game-scale-contact-sheet.png")
        if existing.get("passed") and full_sheet.is_file() and game_sheet.is_file():
            return {"passed": True, "cached": True, "manifest": str(manifest_path.relative_to(REPO_ROOT)), "qa": existing}
        if existing.get("passed"):
            make_direction_contact_sheet(manifest_path, full_sheet, scale=1)
            make_direction_contact_sheet(manifest_path, game_sheet, scale=0.5)
            return {"passed": True, "cached": True, "manifest": str(manifest_path.relative_to(REPO_ROOT)), "qa": existing}
    invoke_blender(blender, renderer, ["--scene", str(scene_path), "--output", str(output), "--expected-armature", rig_spec["skeleton_object"]])
    qa = validate_guide_manifest(manifest_path)
    qa["cache_key"] = cache_seed
    qa["review_contact_sheet"] = "contact-sheet.png"
    qa["game_scale_contact_sheet"] = "game-scale-contact-sheet.png"
    write_json(qa_path, qa)
    if qa["passed"]:
        make_direction_contact_sheet(manifest_path, output / "contact-sheet.png", scale=1)
        make_direction_contact_sheet(manifest_path, output / "game-scale-contact-sheet.png", scale=0.5)
    return {"passed": qa["passed"], "cached": False, "manifest": str(manifest_path.relative_to(REPO_ROOT)), "qa": qa}


def blocked_paint_job(character_id: str, static_review_manifest: Path | None = None) -> dict[str, Any]:
    config_path, config, _, other = load_character(character_id)
    gate = motion_gate(config, other["registry"], REPO_ROOT)
    identity = other["identity"]
    seed = {
        "character_id": character_id,
        "identity_sha256": sha256_file(REPO_ROOT / config["identity"]),
        "identity_reference": identity["reference"],
        "identity_reference_sha256": identity["reference_sha256"],
        "identity_locks": identity["locks"],
        "palette_lock": identity["locks"]["palette"],
        "config_sha256": sha256_file(config_path),
        "required_actions": config["required_actions"],
        "directions": DIRECTIONS,
        "layers": config["paint"]["layers"],
        "semantic_events": config["semantic_events"],
        "motion_blockers": gate["blocked"],
        "legacy_v2_motion_fallback": False,
        "provider": config["paint"]["provider"],
    }
    if static_review_manifest and static_review_manifest.is_file():
        seed["static_review_reference"] = {
            "manifest": str(static_review_manifest.relative_to(REPO_ROOT)),
            "sha256": sha256_file(static_review_manifest),
            "usage": "camera and structural reference only; not an animation paint guide",
        }
    key = hashlib.sha256(json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:24]
    directory = FACTORY_ROOT / "paint-jobs" / f"blocked-{key}"
    job = {
        "schema_version": 1,
        "job_id": key,
        **seed,
        "status": "BLOCKED_MOTIONS_REQUIRED",
        "guide_manifest": None,
        "painted_outputs": [],
        "owner_visual_approval": False,
        "note": "Deterministic waiting record only. It is not a per-frame paint handoff; production guides require approved V3 Idle, Walk, and BasicAttack motions.",
    }
    path = directory / "job.json"
    write_json(path, job)
    return {"passed": False, "status": job["status"], "job_file": str(path.relative_to(REPO_ROOT)), "job_id": key, "blockers": gate["blocked"]}


def run(character_id: str, stage: str, blender: str, force: bool = False) -> tuple[int, dict[str, Any]]:
    report: dict[str, Any] = {"character_id": character_id, "stage": stage}
    preflight = check_preflight(character_id)
    report["preflight"] = preflight
    if not preflight["passed"]:
        return 1, report
    if stage == "preflight":
        return (0 if preflight["motion_gate"]["passed"] else 2), report
    if stage in ("rig", "rig-review", "all"):
        report["rig"] = build_rig(character_id, blender, force=force)
    if stage in ("rig-review", "all"):
        report["rig_review"] = render_rig_review(character_id, blender, force=force)
        if not report["rig_review"]["passed"]:
            return 1, report
    if stage == "handoff":
        # The built-in provider accepts only a real production guide set. Static
        # rig smokes cannot be mistaken for animation-ready painting inputs.
        production_candidates = sorted((FACTORY_ROOT / "renders").glob("*/manifest.json"))
        for manifest_path in production_candidates:
            manifest = read_json(manifest_path)
            if manifest.get("pose_kind") == "PRODUCTION_ANIMATION":
                result = ManualHandoffProvider().prepare(
                    repo_root=REPO_ROOT,
                    config_path=FACTORY_ROOT / "configs" / f"{character_id}.json",
                    guide_manifest_path=manifest_path,
                    output_root=FACTORY_ROOT / "paint-jobs",
                )
                report["paint_handoff"] = result
                return (0 if result["passed"] else 2), report
        report["paint_handoff"] = blocked_paint_job(character_id)
        return 2, report
    if stage == "all":
        static_manifest = REPO_ROOT / report["rig_review"]["manifest"]
        report["paint_handoff"] = blocked_paint_job(character_id, static_manifest)
        report["motion_gate"] = preflight["motion_gate"]
        report["vertical_slice_status"] = "BLOCKED_EXTERNAL_MOTIONS_NOT_ACQUIRED"
        return 2, report
    return 0, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", default="swordsman_male_v3")
    parser.add_argument("--stage", choices=("preflight", "rig", "rig-review", "handoff", "all"), default="all")
    parser.add_argument("--blender", default=os.environ.get("BLENDER_BIN", "blender"))
    parser.add_argument("--force", action="store_true", help="rebuild cached rig or guide outputs")
    args = parser.parse_args()
    try:
        code, report = run(args.character, args.stage, args.blender, args.force)
        print(json.dumps(report, indent=2, sort_keys=True))
        return code
    except Exception as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
