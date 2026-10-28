from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_factory_v3"))

from contracts import cache_key, motion_gate, read_json, repo_path, validate_config, validate_motion_record, validate_rig_spec
from paint_provider import ManualHandoffProvider
from qa import DIRECTIONS, REQUIRED_PASSES, validate_guide_manifest, validate_production_guide_manifest
from import_painted_sheets import ACTIONS as PAINT_ACTIONS, prepare_painted_sheets, write_candidate
from audit_sprite_candidate import audit_definition
from import_layered_sheets import ACTIONS as LAYERED_ACTIONS, CORE_LAYERS, SHEET as LAYERED_SHEET, _clean_cell, _fit_frame, _normalise, _load_sheet, _preserve_cutout_registration
from cutout_master_sheet import cutout_master_sheet
from label_master_from_color_mask import color_mask_to_labels
from normalize_master_sheet import normalize_master_sheet
from refine_headhair_labels import refine_headhair_labels
from sample_motion import sample_clip, validate_sample_timeline


class FactoryContractTests(unittest.TestCase):
    def test_master_normalization_uses_one_transform_and_clears_detached_top_scraps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            master = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
            labels = Image.new("L", (1280, 1280), 0)
            for row in range(8):
                for col in range(8):
                    x, y = col * 160, row * 160
                    ImageDraw.Draw(master).rectangle((x + 60, y + 30, x + 99, y + 69), fill=(190, 150, 90, 255))
                    ImageDraw.Draw(labels).rectangle((x + 60, y + 30, x + 99, y + 69), fill=1)
                    for px, py in ((x + 70, y + 2), (x + 71, y + 2), (x + 70, y + 3), (x + 71, y + 3)):
                        master.putpixel((px, py), (90, 60, 40, 255))
                        labels.putpixel((px, py), 1)
            master_path, labels_path = root / "master.png", root / "labels.png"
            master.save(master_path)
            labels.save(labels_path)

            output_master, output_labels = root / "normalized-master.png", root / "normalized-labels.png"
            report = normalize_master_sheet(master_path, labels_path, output_master, output_labels,
                                            reference_height=32, root_anchor_x=80, root_anchor_y=132,
                                            fragment_limit=10)
            normalized = Image.open(output_master).convert("RGBA")
            normalized_ids = Image.open(output_labels)
            self.assertAlmostEqual(report["shared_scale"], 0.8, places=3)
            self.assertEqual(report["root_anchor_px"], [80, 132])
            self.assertEqual(report["removed_detached_top_body_outfit_pixels"], 8 * 8 * 4)
            self.assertEqual(normalized.getpixel((70, 2))[3], 0)
            self.assertEqual(normalized_ids.getpixel((70, 2)), 0)
            self.assertGreater(normalized.getpixel((80, 131))[3], 0)

    def test_color_mask_labels_preserve_master_alpha_and_assign_unmatched_pixels_to_body(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            master = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
            ImageDraw.Draw(master).rectangle((10, 10, 39, 39), fill=(190, 150, 90, 255))
            ImageDraw.Draw(master).rectangle((50, 50, 79, 79), fill=(190, 150, 90, 255))
            ImageDraw.Draw(master).rectangle((80, 80, 109, 109), fill=(190, 150, 90, 255))
            master_path = root / "master.png"
            master.save(master_path)

            mask = Image.new("RGB", (640, 640), (0, 0, 0))
            draw = ImageDraw.Draw(mask)
            # Input is half-sized to exercise full-sheet registration on resize.
            draw.rectangle((5, 5, 19, 19), fill=(255, 0, 255))
            draw.rectangle((25, 25, 39, 39), fill=(0, 255, 255))
            draw.rectangle((100, 100, 110, 110), fill=(255, 255, 0))  # outside master alpha
            mask_path = root / "mask.png"
            mask.save(mask_path)
            labels_path = root / "labels.png"
            preview_path = root / "preview.png"

            report = color_mask_to_labels(master_path, mask_path, labels_path, preview_path)
            labels = Image.open(labels_path)
            self.assertEqual(labels.size, (1280, 1280))
            self.assertEqual(labels.getpixel((20, 20)), 2)
            self.assertEqual(labels.getpixel((60, 60)), 4)
            self.assertEqual(labels.getpixel((90, 90)), 1)
            self.assertEqual(labels.getpixel((205, 205)), 0)
            self.assertEqual(report["unlabeled_visible_pixels"], 0)
            self.assertEqual(report["label_pixels_outside_master_alpha"], 0)
            self.assertGreater(report["color_mask_pixels_outside_master_alpha"], 0)
            self.assertTrue(preview_path.is_file())

    def test_headhair_refinement_moves_only_nearby_warm_visible_body_pixels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            master = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
            labels = Image.new("L", (1280, 1280), 0)
            draw_master, draw_labels = ImageDraw.Draw(master), ImageDraw.Draw(labels)
            draw_master.rectangle((70, 70, 89, 89), fill=(190, 185, 195, 255))
            draw_labels.rectangle((70, 70, 89, 89), fill=2)
            master.putpixel((80, 92), (210, 150, 110, 255))  # face below hair
            labels.putpixel((80, 92), 1)
            master.putpixel((81, 92), (100, 120, 150, 255))  # cool body pixel
            labels.putpixel((81, 92), 1)
            master.putpixel((100, 92), (210, 150, 110, 255))  # warm, outside ROI
            labels.putpixel((100, 92), 1)
            master_path, labels_path = root / "master.png", root / "labels.png"
            output_path, preview_path = root / "refined.png", root / "preview.png"
            master.save(master_path)
            labels.save(labels_path)

            report = refine_headhair_labels(master_path, labels_path, output_path, preview_path)
            output = Image.open(output_path)
            self.assertEqual(output.getpixel((80, 92)), 2)
            self.assertEqual(output.getpixel((81, 92)), 1)
            self.assertEqual(output.getpixel((100, 92)), 1)
            self.assertEqual(report["moved_face_candidate_pixels"], 1)
            self.assertTrue(preview_path.is_file())

    def test_master_cutout_layers_recompose_exactly_from_one_shared_frame_sheet(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            action_dir = root / "source" / "Idle"
            action_dir.mkdir(parents=True)
            master = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
            labels = Image.new("L", (1280, 1280), 0)
            colors = {
                1: (120, 70, 40, 255), 2: (210, 205, 220, 255), 3: (220, 175, 80, 255),
                4: (190, 200, 210, 255), 5: (245, 185, 45, 255), 6: (255, 245, 205, 220),
                7: (130, 110, 80, 255),
            }
            for row in range(8):
                for col in range(8):
                    for class_id, color in colors.items():
                        x = col * 160 + 10 + class_id * 14
                        y = row * 160 + 20
                        ImageDraw.Draw(master).rectangle((x, y, x + 8, y + 49), fill=color)
                        ImageDraw.Draw(labels).rectangle((x, y, x + 8, y + 49), fill=class_id)
            master_path = action_dir / "master.png"
            labels_path = action_dir / "labels.png"
            master.save(master_path)
            labels.save(labels_path)
            report = cutout_master_sheet(root / "source", root / "cutouts", ["Idle"])
            self.assertEqual(report["actions"]["Idle"]["layers"]["reconstruction_mismatch_pixels"], 0)
            self.assertEqual(report["actions"]["Idle"]["layers"]["unassigned_visible_pixels"], 0)
            for output_name in ("BaseBody", "Hair", "Outfit", "Weapon", "BackAccessory", "CosmeticFX", "Headgear"):
                self.assertTrue((root / "cutouts" / output_name / "idle.png").is_file())
            cutout_sheets = {"Idle": {
                layer: _load_sheet(root / "cutouts" / layer / "idle.png", layer, preserve_source_alpha=True)
                for layer in CORE_LAYERS
            }}
            preserved, registration = _preserve_cutout_registration(cutout_sheets, ("Idle",))
            self.assertEqual(registration["uniform_scale"], 1.0)
            self.assertEqual(registration["registration_policy"].split(";")[0], "preserve full-master pixels, alpha, and frame coordinates")
            self.assertEqual(preserved["Idle"]["BaseBody"].getchannel("A").getpixel((24, 20)), 255)

    def test_master_cutout_rejects_visible_pixels_without_layer_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            action_dir = root / "source" / "Walk"
            action_dir.mkdir(parents=True)
            master = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
            labels = Image.new("L", (1280, 1280), 0)
            master.putpixel((8, 12), (200, 120, 80, 255))
            master.save(action_dir / "master.png")
            labels.save(action_dir / "labels.png")
            with self.assertRaisesRegex(ValueError, "unlabelled pixels"):
                cutout_master_sheet(root / "source", root / "cutouts", ["Walk"])

    def test_layer_fit_applies_one_identical_transform_to_every_part(self):
        cells = {layer: Image.new("RGBA", (160, 160), (0, 0, 0, 0)) for layer in (*CORE_LAYERS, "CosmeticFX")}
        for layer, box in {
            "BaseBody": (50, 30, 110, 150), "Hair": (60, 10, 100, 45),
            "Outfit": (55, 60, 105, 115), "Weapon": (120, 75, 145, 130),
            "BackAccessory": (20, 60, 60, 135), "CosmeticFX": (84, 48, 126, 68),
        }.items():
            ImageDraw.Draw(cells[layer]).rectangle(box, fill=(180, 145, 80, 255))
        guide = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(guide).rectangle((20, 10, 145, 150), fill=(255, 255, 255, 255))
        fitted, report = _fit_frame(cells, (20.0, 10.0, 146.0, 151.0), 1.0)
        self.assertEqual(report["translation"], [0, 0])
        self.assertEqual(report["clipped_layers"], [])
        for layer in cells:
            with self.subTest(layer=layer):
                self.assertEqual(fitted[layer].getchannel("A").tobytes(), cells[layer].getchannel("A").tobytes())

    def test_layer_sheet_normalization_uses_112px_target_and_shared_transform(self):
        sheets = {}
        guides = {}
        for action in LAYERED_ACTIONS:
            layer_sheet = Image.new("RGBA", (LAYERED_SHEET, LAYERED_SHEET), (0, 0, 0, 0))
            guide_sheet = Image.new("RGBA", (LAYERED_SHEET, LAYERED_SHEET), (0, 0, 0, 0))
            for row in range(8):
                for col in range(8):
                    x, y = col * 160, row * 160
                    ImageDraw.Draw(layer_sheet).rectangle((x + 50, y + 24, x + 110, y + 104), fill=(190, 150, 90, 255))
                    ImageDraw.Draw(guide_sheet).rectangle((x + 50, y + 64, x + 110, y + 144), fill=(255, 255, 255, 255))
            sheets[action] = {layer: layer_sheet for layer in (*CORE_LAYERS, "CosmeticFX")}
            guides[action] = guide_sheet
        normalized, report = _normalise(sheets, guides, reference_height=112)
        self.assertEqual(report["frame_count"], 192)
        self.assertEqual(report["target_reference_height_px"], 112)
        self.assertAlmostEqual(report["uniform_scale"], 112 / 81, places=2)
        for action in LAYERED_ACTIONS:
            for layer in CORE_LAYERS:
                self.assertEqual(normalized[action][layer].size, (LAYERED_SHEET, LAYERED_SHEET))

    def test_layer_alpha_cleanup_keeps_disconnected_clothing_but_drops_halo_specks(self):
        source = Image.new("RGBA", (160, 160), (220, 30, 50, 0))
        draw = ImageDraw.Draw(source)
        draw.rectangle((8, 8, 47, 47), fill=(190, 145, 70, 255))
        draw.rectangle((58, 8, 73, 23), fill=(190, 145, 70, 255))
        draw.point((82, 8), fill=(255, 0, 0, 255))
        draw.rectangle((4, 60, 100, 150), fill=(255, 0, 0, 40))
        cleaned = _clean_cell(source, "Outfit")
        alpha = cleaned.getchannel("A")
        self.assertGreater(alpha.getpixel((10, 10)), 0)
        self.assertGreater(alpha.getpixel((60, 10)), 0)
        self.assertEqual(alpha.getpixel((82, 8)), 0)
        self.assertEqual(alpha.getpixel((50, 80)), 0)

    def test_sprite_audit_flags_frame_jumps_without_claiming_art_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            definition_path = repository / "assets/characters/test-swordsman/sprite.json"
            atlas_path = repository / "assets/characters/test-swordsman/atlas.png"
            definition_path.parent.mkdir(parents=True)
            atlas_path.parent.mkdir(parents=True, exist_ok=True)
            atlas = Image.new("RGBA", (32, 16 * len(DIRECTIONS)), (0, 0, 0, 0))
            frames = {}
            for row, direction in enumerate(DIRECTIONS):
                for index in range(2):
                    frame = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
                    from_x = 5 + index
                    for y in range(3, 13):
                        for x in range(from_x, from_x + 5):
                            frame.putpixel((x, y), (220, 150, 60, 255))
                    atlas.paste(frame, (index * 16, row * 16))
                    key = f"test-swordsman_base-body_Idle_{direction}_{index:02d}"
                    frames[key] = {"atlasId": "test-atlas", "rect": [index * 16, row * 16, 16, 16]}
            atlas.save(atlas_path)
            definition = {
                "characterId": "test-swordsman",
                "source": {"status": "DEV_ONLY"},
                "canvas": {"frameWidth": 16, "frameHeight": 16, "rootAnchorX": 8, "rootAnchorY": 14},
                "slots": {"Body": "BaseBody", "Hair": "Hair", "Outfit": "Outfit", "Weapon": "Weapon", "Headgear": "Headgear", "Back": "BackAccessory"},
                "defaultParts": {"Body": "base-body", "Hair": "base-body", "Outfit": "base-body", "Weapon": "base-body", "Headgear": "base-body", "Back": "base-body"},
                "drawOrder": ["Back", "Body", "Hair", "Outfit", "Weapon", "Headgear"],
                "directions": list(DIRECTIONS),
                "clips": {"Idle": {"loop": True, "durations": [100, 100], "directions": {direction: {"frames": [{"frameIndex": i, "sockets": {}} for i in range(2)]} for direction in DIRECTIONS}}},
                "parts": {"base-body": {"slot": "Body", "frames": frames}},
                "atlases": {"test-atlas": {"file": "assets/characters/test-swordsman/atlas.png", "width": 32, "height": 16 * len(DIRECTIONS)}},
            }
            definition_path.write_text(json.dumps(definition), encoding="utf-8")
            result = audit_definition(definition_path)
            self.assertEqual(result["review_status"], "DIAGNOSTIC_ONLY_VISUAL_REVIEW_REQUIRED")
            self.assertAlmostEqual(result["summary"]["Idle"]["silhouette_iou_mean_across_directions"], 0.6667, places=3)
            self.assertEqual(result["summary"]["Idle"]["directions_below_0_88_mean"], list(DIRECTIONS))
            self.assertEqual(result["errors"], [])

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

    def test_retired_v3_guide_preview_is_archived_and_preserved(self):
        candidate = "swordsman-male-v3"
        self.assertFalse((ROOT / "assets/characters" / candidate).exists())
        archive = ROOT / "authoring/characters/factory-v3/unused" / candidate
        path = archive / "sprite.json"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), "5872d665f51c8d4a4bee881fbe6c5b55115f6e0cba7ffca1bd5e5494fb110311")
        definition = read_json(path)
        self.assertEqual(definition["source"]["status"], "DEV_ONLY")
        self.assertIn("INTERNAL_MOTION_REVIEW_CANDIDATE", definition["tags"])
        for atlas in definition["atlases"].values():
            self.assertTrue((archive / "atlases" / Path(atlas["file"]).name).is_file())
        validation = "const fs=require('fs');const api=require('./modular-sprites.js');const e=api.validateDefinition(JSON.parse(fs.readFileSync(process.argv[1])));if(e.length){console.error(e);process.exit(1)}"
        subprocess.run(["node", "-e", validation, str(path)], cwd=ROOT, capture_output=True, text=True, check=True)

    def test_retired_painted_candidates_are_archived_and_unavailable_to_runtime(self):
        archived = ROOT / "authoring/characters/factory-v3/unused"
        candidates = {
            "swordsman-male-v3-painted": "17babba4bebc7589912ceb58b116ba7baa9e4bbde6b6204db515f1221a29cf5a",
            "swordsman-male-v3-painted-v2": "81e12b648d8a99152033985544eeb7f8d44811d0b9ef1d592b0fc6b5a7336f49",
        }
        for candidate, digest in candidates.items():
            with self.subTest(candidate=candidate):
                self.assertFalse((ROOT / "assets/characters" / candidate).exists())
                path = archived / candidate / "sprite.json"
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                definition = read_json(path)
                self.assertIn("FUSED_BODY_OUTFIT_HAIR_WEAPON", definition["tags"])
                self.assertFalse(definition["source"].get("approvedBy"))
                for atlas in definition["atlases"].values():
                    self.assertTrue((archived / candidate / "atlases" / Path(atlas["file"]).name).is_file())
        self.assertTrue((ROOT / "authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/SE/Master/000.png").is_file())
        for candidate in [*candidates, "swordsman-male-v3"]:
            with self.assertRaisesRegex(ValueError, "Retired character IDs"):
                write_candidate(ROOT, ROOT / "unused-output", candidate, ROOT / "missing.json", {})

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


class PaintedSheetNormalizationTests(unittest.TestCase):
    def test_one_scale_alpha_cleanup_and_all_192_cells(self):
        from PIL import ImageDraw

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            painted_paths, guide_paths = {}, {}
            for action in PAINT_ACTIONS:
                painted = Image.new("RGBA", (640, 640), (255, 0, 255, 127))
                guide = Image.new("RGBA", (1280, 1280), (0, 0, 0, 0))
                for row in range(8):
                    for column in range(8):
                        ImageDraw.Draw(painted).rectangle((column * 80 + 10, row * 80 + 10, column * 80 + 30, row * 80 + 50), fill=(80, 100, 120, 255))
                        ImageDraw.Draw(guide).rectangle((column * 160 + 20, row * 160 + 20, column * 160 + 60, row * 160 + 100), fill=(255, 255, 255, 255))
                painted_paths[action] = root / f"{action}-paint.png"
                guide_paths[action] = root / f"{action}-guide.png"
                painted.save(painted_paths[action])
                guide.save(guide_paths[action])

            normalized, report = prepare_painted_sheets(painted_paths, guide_paths, root / "normalized")
            self.assertEqual(report["normalized_frame_count"], 192)
            self.assertEqual(len({frame["scale"] for frame in report["frames"]}), 1)
            self.assertAlmostEqual(report["uniform_character_scale"], 81 / 84, places=3)
            self.assertEqual(normalized["Idle"].getpixel((0, 0))[3], 0)
            first_cell = normalized["Idle"].crop((0, 0, 160, 160))
            self.assertIsNotNone(first_cell.getchannel("A").getbbox())
            first_frame = next(frame for frame in report["frames"] if frame["action"] == "Idle" and frame["direction"] == "S" and frame["frame_index"] == 0)
            left, top, right, bottom = first_frame["normalized_bbox"]
            guide_left, guide_top, guide_right, guide_bottom = first_frame["guide_bbox"]
            self.assertGreaterEqual(left, guide_left - 6)
            self.assertGreaterEqual(top, guide_top - 6)
            self.assertLessEqual(right, guide_right + 6)
            self.assertLessEqual(bottom, guide_bottom + 6)


if __name__ == "__main__":
    unittest.main()
