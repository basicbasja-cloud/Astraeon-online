from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_factory_v3"))

from contracts import cache_key, motion_gate, read_json, repo_path, validate_config, validate_motion_record, validate_rig_spec
from paint_provider import ManualHandoffProvider
from qa import DIRECTIONS, REQUIRED_PASSES, validate_guide_manifest, validate_production_guide_manifest
from sample_motion import sample_clip, validate_sample_timeline


class FactoryContractTests(unittest.TestCase):
    def test_character_and_rig_contracts_validate(self):
        config = read_json(ROOT / "authoring/characters/factory-v3/configs/swordsman_male_v3.json")
        rig = read_json(ROOT / "authoring/characters/factory-v3/rigs/astraeon_humanoid_male_v1.json")
        self.assertEqual(validate_config(config), [])
        self.assertEqual(validate_rig_spec(rig), [])
        self.assertEqual(rig["validation"]["expected_bone_count"], 60)

    def test_config_actions_match_free_motion_selections(self):
        config = read_json(ROOT / "authoring/characters/factory-v3/configs/swordsman_male_v3.json")
        selections = read_json(ROOT / "authoring/characters/factory-v3/motions/selections.json")
        for action in config["required_actions"]:
            with self.subTest(action=action):
                self.assertEqual(config["actions"][action]["motion_id"], selections["actions"][action]["motion_id"])

    def test_repo_path_rejects_parent_escape(self):
        with self.assertRaises(ValueError):
            repo_path(ROOT, "../../outside.blend")

    def test_motion_gate_requires_real_hash_and_license_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            motion_path = root / "motions/raw/walk.fbx"
            license_path = root / "licenses/terms.txt"
            motion_path.parent.mkdir(parents=True)
            license_path.parent.mkdir(parents=True)
            motion_bytes = b"sample motion bytes"
            motion_path.write_bytes(motion_bytes)
            license_path.write_text("Reviewed license terms", encoding="utf-8")
            digest = hashlib.sha256(motion_bytes).hexdigest()
            record = {
                "id": "walk_v3",
                "provider": "Example Provider",
                "source_title": "Walk source",
                "source_url": "https://example.invalid/walk",
                "acquisition_date": "2026-10-19",
                "original_filename": "walk.fbx",
                "file_sha256": digest,
                "original_skeleton": ["Hips", "Spine"],
                "source_format": "FBX",
                "original_fps": 30,
                "duration_seconds": 1.6,
                "loop": True,
                "license_summary": "Commercial use and retargeting reviewed.",
                "commercial_use_status": "APPROVED",
                "retarget_permission_status": "APPROVED",
                "modification_status": "RETARGET_AND_STYLIZATION_REVIEWED",
                "production_status": "APPROVED_FOR_PRODUCTION",
                "local_path": "motions/raw/walk.fbx",
                "license_evidence": ["licenses/terms.txt"],
            }
            config = {"required_actions": ["Walk"], "actions": {"Walk": {"motion_id": "walk_v3"}}}
            registry = {"imported_motions": [record]}
            self.assertTrue(motion_gate(config, registry, root)["passed"])
            motion_path.write_bytes(b"changed after approval")
            gate = motion_gate(config, registry, root)
            self.assertFalse(gate["passed"])
            self.assertIn("hash does not match", gate["blocked"][0]["issues"][0])

    def test_production_approval_requires_evidence_fields(self):
        result = validate_motion_record({"id": "partial", "production_status": "APPROVED_FOR_PRODUCTION"})
        self.assertTrue(any("license_evidence" in issue for issue in result))
        self.assertTrue(any("file_sha256" in issue for issue in result))

    def test_canonical_rig_manifest_is_action_free(self):
        manifest = read_json(ROOT / "authoring/characters/factory-v3/manifests/astraeon_humanoid_male_v1.rig.json")
        self.assertEqual(manifest["bone_count"], 60)
        self.assertEqual(manifest["remaining_action_count"], 0)

    def test_imported_motion_provenance_hashes_and_evidence_are_valid(self):
        registry = read_json(ROOT / "authoring/characters/factory-v3/motions/candidates.json")
        records = registry["imported_motions"]
        self.assertGreaterEqual(len(records), 3)
        for record in records:
            self.assertEqual(validate_motion_record(record), [], record["id"])
            self.assertRegex(record["file_sha256"], re.compile(r"^[0-9a-f]{64}$"))
            for evidence in record["license_evidence"]:
                path = Path(evidence)
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                self.assertTrue((ROOT / path).is_file(), evidence)

    def test_registered_profiles_cover_canonical_motion_bones(self):
        profiles = read_json(ROOT / "authoring/characters/factory-v3/motions/retarget-profiles.json")["profiles"]
        required = {
            "root", "Hips", "Spine", "Chest", "Neck", "Head", "Clavicle.L", "UpperArm.L",
            "Forearm.L", "Hand.L", "Clavicle.R", "UpperArm.R", "Forearm.R", "Hand.R",
            "Thigh.L", "Shin.L", "Foot.L", "Thigh.R", "Shin.R", "Foot.R",
        }
        for profile_id, profile in profiles.items():
            with self.subTest(profile=profile_id):
                self.assertTrue(required.issubset(profile["motion_bones"]))

    def test_mixamo_profile_resolves_namespaced_and_plain_fbx_bones(self):
        profile = read_json(ROOT / "authoring/characters/factory-v3/motions/retarget-profiles.json")["profiles"]["mixamo_fbx"]
        self.assertEqual(profile["format"], "FBX")
        self.assertEqual(profile["source_root_bone"], ["mixamorig:Hips", "Hips"])
        self.assertEqual(profile["motion_bones"]["Chest"], ["mixamorig:Spine2", "Spine2", "mixamorig:Spine1", "Spine1"])
        for target, aliases in profile["motion_bones"].items():
            with self.subTest(target=target):
                self.assertIsInstance(aliases, list)
                self.assertGreaterEqual(len(aliases), 2)
        self.assertEqual(profile["height_foot_bones"][0], ["mixamorig:LeftToeBase", "LeftToeBase"])

    def test_mesh2motion_glb_profile_maps_human_rig_and_separate_actions(self):
        profile = read_json(ROOT / "authoring/characters/factory-v3/motions/retarget-profiles.json")["profiles"]["mesh2motion_human_glb"]
        self.assertEqual(profile["format"], "GLB")
        self.assertEqual(profile["source_root_bone"], "root")
        self.assertEqual(profile["motion_bones"]["Hips"], "pelvis")
        self.assertEqual(profile["motion_bones"]["Thigh.L"], "thigh_l")
        self.assertEqual(profile["motion_bones"]["Hand.R"], "hand_r")
        self.assertEqual(profile["height_foot_bones"], ["ball_l", "ball_r"])

    def test_runtime_package_passes_the_existing_javascript_contract(self):
        result = subprocess.run(
            ["node", str(ROOT / "tools/character_factory_v3/validate_runtime_package.cjs"),
             "assets/characters/swordsman-male-v3/sprite.json"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        report = json.loads(result.stdout)
        self.assertTrue(report["passed"], report["errors"])
        self.assertEqual(report["canvas"], {"frameWidth": 160, "frameHeight": 160, "rootAnchorX": 80, "rootAnchorY": 132, "referenceHeight": 88})
        self.assertEqual(report["directions"], list(DIRECTIONS))
        self.assertLess(report["decoded_atlas_bytes"], 80 * 1024 * 1024)
        definition = read_json(ROOT / "assets/characters/swordsman-male-v3/sprite.json")
        self.assertEqual(definition["source"]["status"], "DEV_ONLY")
        self.assertFalse(definition["source"].get("approvedBy"))
        self.assertIn("INTERNAL_MOTION_REVIEW_CANDIDATE", definition["tags"])
        for clip in definition["clips"].values():
            total = sum(clip["durations"])
            for event in clip.get("events", []):
                self.assertLessEqual(event["timeMs"], total)
                self.assertLess(event["frameIndex"], len(clip["durations"]))

    def test_cache_key_changes_with_input_hashes(self):
        args = dict(
            source_hashes={"source": "a"}, rig_hash="b", motion_hash="c", retarget={},
            cleanup={}, stylization={}, camera={}, prop_hash="d", sampler={}, script_hashes={},
        )
        self.assertEqual(cache_key(**args), cache_key(**args))
        changed = dict(args, motion_hash="different")
        self.assertNotEqual(cache_key(**args), cache_key(**changed))


class SamplingTests(unittest.TestCase):
    def test_walk_sampling_keeps_source_fps_separate_and_sets_durations(self):
        result = sample_clip(
            "Walk",
            {"motion_id": "walk_v3", "sample_count": 8, "loop": True},
            {"source_fps": 30, "frame_start": 1, "frame_end": 48, "semantic_events": [{"name": "footstep", "phase": 0.25}]},
            [0.0, 0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88],
        )
        self.assertEqual(result["source_fps"], 30)
        self.assertEqual(result["frame_count"], 8)
        self.assertTrue(all(frame["duration_ms"] > 0 for frame in result["frames"]))
        self.assertEqual(validate_sample_timeline(result), [])
        self.assertEqual(result["events"][0]["name"], "footstep")

    def test_attack_sampling_requires_reviewed_phase_markers(self):
        action = {"motion_id": "attack_v3", "sample_count": 8, "loop": False}
        with self.assertRaisesRegex(ValueError, "semantic phase markers"):
            sample_clip("BasicAttack", action, {"source_fps": 30, "frame_start": 1, "frame_end": 30}, [0, .12, .25, .38, .5, .62, .75, .88])
        clip = {
            "source_fps": 30,
            "frame_start": 1,
            "frame_end": 48,
            "semantic_phases": {"anticipation": .1, "wind_up": .25, "contact": .5, "follow_through": .65, "recovery": .82},
            "semantic_events": [{"name": "contact", "phase": .5}],
        }
        result = sample_clip("BasicAttack", action, clip, [0, .12, .25, .38, .5, .62, .75, .88])
        self.assertEqual(result["frame_count"], 8)
        self.assertIn("contact", [event["name"] for event in result["events"]])
        self.assertGreaterEqual(result["frames"][-1]["duration_ms"], 30)
        self.assertEqual(result["duration_ms"], 1600)
        self.assertEqual(validate_sample_timeline(result), [])


class GuideQaTests(unittest.TestCase):
    def create_static_manifest(self, root: Path) -> Path:
        frames = []
        for direction in DIRECTIONS:
            pass_records = {}
            for pass_name in REQUIRED_PASSES:
                relative = Path(direction) / f"{pass_name}.png"
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new("RGBA", (320, 320), (255, 255, 255, 0))
                if pass_name in ("rgb", "silhouette", "body_segmentation", "weapon_mask"):
                    image.putpixel((100, 100), (255, 255, 255, 255))
                image.save(path)
                pass_records[pass_name] = {"file": relative.as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            frames.append({
                "direction": direction,
                "frame_index": 0,
                "yaw_degrees": {"S": 0, "SW": -45, "W": -90, "NW": -135, "N": -180, "NE": -225, "E": -270, "SE": 45}[direction],
                "visible_alpha_pixels": 1,
                "object_index_values": [1, 4],
                "passes": pass_records,
            })
        manifest = {
            "pose_kind": "REST_ONLY_NONPRODUCTION",
            "width": 320,
            "height": 320,
            "directions": list(DIRECTIONS),
            "mirroring": "none",
            "root_pixel": [160, 264],
            "frames": frames,
        }
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_static_guide_manifest_checks_every_direction_and_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = self.create_static_manifest(Path(temp))
            self.assertTrue(validate_guide_manifest(manifest)["passed"])
            self.assertFalse(validate_production_guide_manifest(manifest, ["Idle", "Walk", "BasicAttack"])["passed"])

    def test_static_manifest_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = self.create_static_manifest(Path(temp))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["frames"][0]["passes"]["rgb"]["file"] = "../../outside.png"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = validate_guide_manifest(manifest_path)
            self.assertFalse(report["passed"])
            self.assertTrue(any("Unsafe pass path" in error for error in report["errors"]))

    def test_manual_provider_rejects_static_rig_smoke(self):
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            manifest = self.create_static_manifest(temporary)
            result = ManualHandoffProvider().prepare(
                repo_root=ROOT,
                config_path=ROOT / "authoring/characters/factory-v3/configs/swordsman_male_v3.json",
                guide_manifest_path=manifest,
                output_root=temporary / "paint-jobs",
            )
            self.assertFalse(result["passed"])
            self.assertIn("complete animated guide set", result["blocked"])
            self.assertFalse((temporary / "paint-jobs").exists())


if __name__ == "__main__":
    unittest.main()
