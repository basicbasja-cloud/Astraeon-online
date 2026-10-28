#!/usr/bin/env python3
"""Config-driven command line entry point for Astraeon Character Factory V3."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from contracts import (
    DIRECTIONS,
    cache_key,
    motion_gate,
    read_json,
    sha256_file,
    validate_config,
    validate_motion_record,
    validate_rig_spec,
    write_json,
)
from paint_provider import ManualHandoffProvider
from qa import make_direction_contact_sheet, make_motion_contact_sheet, validate_guide_manifest, validate_production_guide_manifest
from sample_motion import sample_clip, validate_sample_timeline


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


def write_motion_build_evidence(
    config: dict[str, Any],
    rig_spec: dict[str, Any],
    selections: dict[str, Any],
    profile_reports: dict[str, dict[str, Any]],
    manifest_path: Path,
    qa: dict[str, Any],
    runtime_definition: Path,
    runtime_validation: dict[str, Any],
    paint_report: dict[str, Any],
) -> Path:
    manifest = read_json(manifest_path)
    actions = {}
    for action_name, rendered in manifest["actions"].items():
        item = profile_reports[action_name]
        retarget = item["retarget_report"]
        timeline = item["timeline"]
        actions[action_name] = {
            "motion_provenance": item["motion_provenance"],
            "selection_review": selections["actions"][action_name].get("visual_review"),
            "retarget": {
                "passed": retarget["qa"].get("passed") is True,
                "root_stable": retarget["qa"].get("root_stable_for_in_place") is True,
                "output_scene_sha256": retarget.get("output_scene_sha256"),
                "source_action": retarget.get("source_action"),
                "source_action_internal_name": retarget.get("source_action_internal_name"),
                "source_bone_mapping": retarget.get("source_bone_mapping", {}),
                "mapped_required_bones": retarget["qa"].get("mapped_required_bones", []),
                "max_rendered_root_horizontal_excursion": retarget.get("max_rendered_root_horizontal_excursion"),
            },
            "foot_contacts": rendered.get("foot_contacts", {}),
            "sampling": {
                "frame_count": timeline["frame_count"],
                "durations_ms": [frame["duration_ms"] for frame in timeline["frames"]],
                "duration_ms": timeline["duration_ms"],
                "source_fps": timeline["source_fps"],
                "output_fps": timeline["output_fps"],
                "loop": timeline["loop"],
                "semantic_phases": timeline["semantic_phases"],
                "events": timeline["events"],
            },
            "rendered_events": rendered.get("events", []),
        }
    evidence = {
        "schema_version": 1,
        "character_id": config["id"],
        "status": "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING",
        "owner_approved": False,
        "runtime_admitted": False,
        "legacy_v2_motion_fallback": False,
        "rig": {
            "id": rig_spec["id"],
            "bone_count": rig_spec["validation"]["expected_bone_count"],
            "bone_names": rig_spec["bones"],
            "removed_v2_action_count": read_json(FACTORY_ROOT / "manifests" / "astraeon_humanoid_male_v1.rig.json").get("removed_action_count"),
            "remaining_action_count": read_json(FACTORY_ROOT / "manifests" / "astraeon_humanoid_male_v1.rig.json").get("remaining_action_count"),
        },
        "actions": actions,
        "guides": {
            "manifest": str(manifest_path.relative_to(REPO_ROOT)),
            "manifest_sha256": sha256_file(manifest_path),
            "qa_passed": qa.get("passed") is True,
            "directions": manifest.get("directions", []),
            "mirroring": manifest.get("mirroring"),
            "frame_record_count": len(manifest.get("frames", [])),
            "structural_passes": list(manifest.get("frames", [{}])[0].get("passes", {}).keys()),
            "contact_sheets": qa.get("review_contact_sheets", {}),
            "game_scale_contact_sheets": qa.get("game_scale_contact_sheets", {}),
        },
        "paint_candidate": {
            "status": "PROCEDURAL_REVIEW_CANDIDATE",
            "palette_colors": paint_report.get("palette_colors"),
            "palette_source_frames": paint_report.get("palette_source_frames"),
            "actions": paint_report.get("actions", {}),
            "placeholder_actions": paint_report.get("placeholder_actions", []),
            "layer_limits": paint_report.get("layer_limits", {}),
            "stylization": paint_report.get("stylization"),
        },
        "runtime": {
            "definition": str(runtime_definition.relative_to(REPO_ROOT)),
            "definition_sha256": sha256_file(runtime_definition),
            "schema_passed": runtime_validation.get("passed") is True,
            "canvas": runtime_validation.get("canvas"),
            "decoded_atlas_bytes": runtime_validation.get("decoded_atlas_bytes"),
            "action_count": runtime_validation.get("action_count"),
        },
        "source_mesh_limitations": manifest.get("logical_layer_limits", {}),
    }
    output = REPO_ROOT / "docs" / "character-factory" / "evidence" / "production-factory-v3-motion.json"
    write_json(output, evidence)
    return output


def build_motion_pipeline(character_id: str, blender: str, force: bool = False) -> dict[str, Any]:
    config_path, config, rig_spec, other = load_character(character_id)
    registry = other["registry"]
    selection_path = FACTORY_ROOT / "motions" / "selections.json"
    selections = read_json(selection_path)
    imported = {record.get("id"): record for record in registry.get("imported_motions", [])}
    rig_scene = REPO_ROOT / config["rig"]["scene"]
    if not rig_scene.is_file():
        raise FileNotFoundError(f"Action-free V3 rig is missing: {rig_scene}")
    profiles_path = FACTORY_ROOT / "motions" / "retarget-profiles.json"
    retarget_script = BLENDER_ROOT / "retarget_motion.py"
    sample_script = TOOL_ROOT / "sample_motion.py"
    profiles = read_json(profiles_path)
    profile_reports = {}
    retarget_root = FACTORY_ROOT / "motions" / "retargeted"
    retarget_root.mkdir(parents=True, exist_ok=True)

    for action_name in config["required_actions"]:
        selection = selections.get("actions", {}).get(action_name)
        if not selection:
            raise ValueError(f"No selected free motion for required action {action_name}")
        motion_id = selection["motion_id"]
        record = imported.get(motion_id)
        if not record:
            raise ValueError(f"Selected motion has no provenance record: {motion_id}")
        issues = validate_motion_record(record)
        if issues:
            raise ValueError(f"Selected motion provenance is incomplete for {motion_id}:\n- " + "\n- ".join(issues))
        if record.get("production_status") not in ("CANDIDATE", "APPROVED_FOR_PRODUCTION"):
            raise ValueError(f"Selected motion is not eligible for internal review: {motion_id}")
        if record.get("local_path") != selection.get("source_path") or record.get("file_sha256") != selection.get("source_sha256"):
            raise ValueError(f"Selection/provenance source lock differs for {motion_id}")
        source_path = REPO_ROOT / selection["source_path"]
        if not source_path.is_file():
            raise FileNotFoundError(f"Free motion source is missing from local intake: {source_path}")
        if sha256_file(source_path) != selection["source_sha256"]:
            raise ValueError(f"Selected source digest changed for {motion_id}")
        profile_id = selection["profile_id"]
        profile = profiles["profiles"].get(profile_id)
        if not profile:
            raise ValueError(f"No retarget profile is registered for {profile_id}")
        report_path = retarget_root / f"{action_name.lower()}.retarget.json"
        scene_path = retarget_root / f"{action_name.lower()}.blend"
        cached = False
        if report_path.is_file() and scene_path.is_file() and not force:
            old = read_json(report_path)
            cached = all((
                old.get("source_sha256") == selection["source_sha256"],
                old.get("rig_scene_sha256") == sha256_file(rig_scene),
                old.get("profile_sha256") == sha256_file(profiles_path),
                old.get("profile_id") == profile_id,
                old.get("retarget_script_sha256") == sha256_file(retarget_script),
                old.get("output_scene_sha256") == sha256_file(scene_path),
                selection.get("source_action") is None or old.get("source_action") == selection.get("source_action"),
                old.get("qa", {}).get("passed") is True,
            ))
        if not cached:
            command_args = [
                "--rig-scene", str(rig_scene), "--source", str(source_path),
                "--profile", str(profiles_path), "--profile-id", profile_id,
                "--motion-id", motion_id, "--source-sha256", selection["source_sha256"],
                "--output-scene", str(scene_path), "--report", str(report_path),
                "--root-policy", "in_place",
            ]
            if selection.get("source_fps"):
                command_args.extend(["--source-fps", str(selection["source_fps"])])
            if selection.get("source_action"):
                command_args.extend(["--source-action-name", selection["source_action"]])
            invoke_blender(blender, retarget_script, command_args)
        retarget_report = read_json(report_path)
        if not retarget_report.get("qa", {}).get("passed"):
            raise RuntimeError(f"Retarget QA failed for {action_name}: {retarget_report.get('qa')}")

        sampling_clip = {
            **retarget_report,
            "semantic_phases": selection.get("semantic_phases", {}),
            "semantic_events": selection.get("semantic_events", []),
        }
        if selection.get("retarget_frame_range"):
            action_config = {**config["actions"][action_name], "retarget_frame_range": selection["retarget_frame_range"]}
        else:
            action_config = config["actions"][action_name]
        timeline = sample_clip(action_name, action_config, sampling_clip, config["sampling"]["default_phase_samples"])
        timeline["character_id"] = config["id"]
        timeline["directions"] = config["render"]["directions"]
        timeline["frame_size"] = [config["render"]["width"], config["render"]["height"]]
        timeline["status"] = "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING"
        timeline_errors = validate_sample_timeline(timeline)
        if timeline_errors:
            raise ValueError(f"Sampled timeline failed for {action_name}:\n- " + "\n- ".join(timeline_errors))
        timeline_path = retarget_root / f"{action_name.lower()}.timeline.json"
        write_json(timeline_path, timeline)
        profile_reports[action_name] = {
            "scene": str(scene_path),
            "timeline": timeline,
            "motion_provenance": record,
            "retarget_report": retarget_report,
            "retarget_report_path": str(report_path),
            "source_root_motion": retarget_report.get("root_motion_source_axes", {}),
            "foot_contacts": retarget_report.get("foot_contacts", {}),
            "qa": retarget_report.get("qa", {}),
        }

    guide_input_path = retarget_root / "guide-input.json"
    guide_input = {
        "schema_version": 1,
        "rig_spec": rig_spec,
        "actions": profile_reports,
    }
    write_json(guide_input_path, guide_input)
    renderer = BLENDER_ROOT / "render_guides.py"
    motion_hash = hashlib.sha256(json.dumps({
        action: {
            "source": item["motion_provenance"]["file_sha256"],
            "report": item["retarget_report"]["output_scene_sha256"],
            "timeline": item["timeline"],
        }
        for action, item in profile_reports.items()
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    guide_key = cache_key(
        source_hashes={
            "rig_scene": sha256_file(rig_scene),
            "rig_spec": sha256_file(REPO_ROOT / config["rig"]["spec"]),
            "character_config": sha256_file(config_path),
            "selections": sha256_file(selection_path),
            "retarget_profiles": sha256_file(profiles_path),
        },
        rig_hash=sha256_file(rig_scene),
        motion_hash=motion_hash,
        retarget={action: item["retarget_report"]["qa"] for action, item in profile_reports.items()},
        cleanup={"old_v2_actions": "forbidden", "root_policy": "in_place", "cmu_added_rest_frame": "excluded"},
        stylization={profile_id: profiles["profiles"][profile_id].get("stylization", {}) for profile_id in sorted({selection["profile_id"] for selection in selections["actions"].values()})},
        camera=rig_spec["render_contract"],
        prop_hash="CANONICAL_V3_SWORD_AND_CAPE",
        sampler=config["sampling"],
        script_hashes={
            "retarget_motion.py": sha256_file(retarget_script),
            "render_guides.py": sha256_file(renderer),
            "sample_motion.py": sha256_file(sample_script),
            "qa.py": sha256_file(TOOL_ROOT / "qa.py"),
            "contracts.py": sha256_file(TOOL_ROOT / "contracts.py"),
            "run.py": sha256_file(TOOL_ROOT / "run.py"),
        },
    )[:16]
    guide_root = FACTORY_ROOT / "renders" / f"animation-{guide_key}"
    manifest_path = guide_root / "manifest.json"
    qa_path = guide_root / "qa.json"
    cached_guide = manifest_path.is_file() and qa_path.is_file() and not force and read_json(qa_path).get("passed") is True
    if not cached_guide:
        if guide_root.exists():
            shutil.rmtree(guide_root)
        invoke_blender(blender, renderer, ["--timelines", str(guide_input_path), "--output", str(guide_root), "--expected-armature", rig_spec["skeleton_object"]])
    qa = validate_production_guide_manifest(manifest_path, config["required_actions"])
    qa["cache_key"] = guide_key
    qa["review_contact_sheets"] = {}
    qa["game_scale_contact_sheets"] = {}
    write_json(qa_path, qa)
    if not qa["passed"]:
        raise RuntimeError("Rendered V3 animation guides failed structural QA:\n- " + "\n- ".join(qa["errors"]))
    for action in config["required_actions"]:
        full_sheet = guide_root / f"contact-sheet-{action.lower()}.png"
        game_sheet = guide_root / f"game-scale-contact-sheet-{action.lower()}.png"
        if force or not full_sheet.is_file():
            make_motion_contact_sheet(manifest_path, action, full_sheet, scale=1.0)
        if force or not game_sheet.is_file():
            make_motion_contact_sheet(manifest_path, action, game_sheet, scale=0.5)
        qa["review_contact_sheets"][action] = str(full_sheet.relative_to(REPO_ROOT))
        qa["game_scale_contact_sheets"][action] = str(game_sheet.relative_to(REPO_ROOT))
    write_json(qa_path, qa)

    if config["output"]["runtime_character_id"] in {"swordsman-male-v3", "swordsman-male-v3-painted", "swordsman-male-v3-painted-v2"}:
        raise RuntimeError("Retired preview runtime ID: choose a new approved character output; preserved motion guides remain available")
    paint_handoff = ManualHandoffProvider().prepare(
        repo_root=REPO_ROOT,
        config_path=config_path,
        guide_manifest_path=manifest_path,
        output_root=FACTORY_ROOT / "paint-jobs",
    )
    staging = Path(tempfile.gettempdir()) / f"astraeon-factory-v3-paint-{guide_key}"
    if force and staging.exists():
        shutil.rmtree(staging)
    painter = TOOL_ROOT / "paint_runtime.py"
    paint_command = [sys.executable, str(painter), "--manifest", str(manifest_path), "--output", str(staging), "--repository", str(REPO_ROOT)]
    paint_result = subprocess.run(paint_command, cwd=REPO_ROOT, capture_output=True, text=True)
    if paint_result.returncode:
        raise RuntimeError("Deterministic V3 paint candidate failed:\n" + paint_result.stdout + paint_result.stderr)
    packer = REPO_ROOT / "tools" / "pack-modular-sprites.py"
    pack_result = subprocess.run(
        [sys.executable, str(packer), "--definition", str(staging / "sprite-definition.json"), "--sources", str(staging), "--repository", str(REPO_ROOT), "--deduplicate"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if pack_result.returncode:
        raise RuntimeError("V3 runtime sprite packing failed:\n" + pack_result.stdout + pack_result.stderr)
    runtime_definition = REPO_ROOT / "assets" / "characters" / config["output"]["runtime_character_id"] / "sprite.json"
    runtime_validator = TOOL_ROOT / "validate_runtime_package.cjs"
    runtime_validation = subprocess.run(
        ["node", str(runtime_validator), str(runtime_definition)],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if runtime_validation.returncode:
        raise RuntimeError("V3 runtime package validation failed:\n" + runtime_validation.stdout + runtime_validation.stderr)
    runtime_validation_report = json.loads(runtime_validation.stdout)
    paint_report = json.loads(paint_result.stdout)
    evidence_path = write_motion_build_evidence(
        config, rig_spec, selections, profile_reports, manifest_path, qa,
        runtime_definition, runtime_validation_report, paint_report,
    )
    provenance_sidecar = runtime_definition.parent / "motion-provenance.json"
    return {
        "passed": True,
        "status": "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING",
        "cache_key": guide_key,
        "cached_retarget_and_guides": cached_guide,
        "manifest": str(manifest_path.relative_to(REPO_ROOT)),
        "qa": qa,
        "paint_handoff": paint_handoff,
        "procedural_paint_candidate": paint_result.stdout.strip(),
        "runtime_definition": str(runtime_definition.relative_to(REPO_ROOT)),
        "runtime_validation": runtime_validation.stdout.strip(),
        "evidence": str(evidence_path.relative_to(REPO_ROOT)),
        "motion_provenance_sidecar": str(provenance_sidecar.relative_to(REPO_ROOT)),
        "runtime_pack": pack_result.stdout.strip(),
        "owner_approved": False,
        "runtime_admitted": False,
    }


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
    if stage == "motion-build":
        report["rig"] = build_rig(character_id, blender, force=force)
        report["motion_pipeline"] = build_motion_pipeline(character_id, blender, force=force)
        report["motion_gate"] = check_preflight(character_id)["motion_gate"]
        report["vertical_slice_status"] = "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING"
        return 0, report
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
        report["motion_pipeline"] = build_motion_pipeline(character_id, blender, force=force)
        report["motion_gate"] = preflight["motion_gate"]
        report["vertical_slice_status"] = "INTERNAL_VISUAL_CANDIDATE_OWNER_APPROVAL_PENDING"
        return 0, report
    return 0, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", default="swordsman_male_v3")
    parser.add_argument("--stage", choices=("preflight", "rig", "rig-review", "motion-build", "handoff", "all"), default="all")
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
