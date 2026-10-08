import json
import math
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if ROOT.name == "tests":
    ROOT = ROOT.parent
if (ROOT / "tools").exists():
    sys.path.insert(0, str(ROOT / "tools"))
try:
    import build_true_modular_swordsman_v2 as swordsman
except ImportError:
    import build_true_modular_swordsman as swordsman
from modular_character_engine import CANONICAL_DIRECTIONS, validate_blueprint
blueprint_path = ROOT / "authoring/characters/true-modular/swordsman/male/blueprint.json"
if not blueprint_path.exists():
    blueprint_path = ROOT / "swordsman-male-blueprint.json"
SPEC = json.loads(blueprint_path.read_text())
PACKAGE = ROOT / "authoring/characters/true-modular/swordsman/male"


class BlueprintContractTests(unittest.TestCase):
    def test_blueprint_is_valid_and_keeps_art_layers_modular(self):
        validate_blueprint(SPEC)
        self.assertEqual(SPEC["directions"], CANONICAL_DIRECTIONS)
        self.assertEqual(len(SPEC["authoringLayers"]), 11)
        self.assertIn("BodyCore", [part["id"] for part in SPEC["authoringLayers"]])
        self.assertIn("HeadBase", [part["id"] for part in SPEC["authoringLayers"]])
        self.assertNotEqual(SPEC["runtimeCompile"]["BaseBody"], ["BodyCore"])

    def test_release_actions_are_separate_from_optional_and_other_class_actions(self):
        self.assertEqual(len(SPEC["clips"]), 18)
        self.assertEqual(len(SPEC["releaseRequiredClips"]), 16)
        self.assertIn("Sit", SPEC["optionalSupportedClips"])
        self.assertIn("Blink", SPEC["classExcludedClips"])
        self.assertNotIn("Blink", SPEC["releaseRequiredClips"])

    def test_blueprint_rejects_mirroring_and_bad_runtime_compile(self):
        bad = json.loads(json.dumps(SPEC))
        bad["registration"]["mirroring"] = "horizontal"
        with self.assertRaises(ValueError):
            validate_blueprint(bad)
        bad = json.loads(json.dumps(SPEC))
        bad["runtimeCompile"]["Hair"].remove("HairFront")
        with self.assertRaises(ValueError):
            validate_blueprint(bad)


class SharedPoseRigTests(unittest.TestCase):
    def test_all_walk_and_idle_frames_share_canvas_root_and_pose_identity(self):
        for direction in CANONICAL_DIRECTIONS:
            counts = {"Idle": 8, "Walk": 16}
            for clip, count in counts.items():
                for frame in range(count):
                    pose = swordsman.pose_for(direction, clip, frame)
                    self.assertEqual(pose["direction"], direction)
                    self.assertEqual(pose["clip"], clip)
                    self.assertEqual(pose["frame"], frame)
                    self.assertEqual(pose["root"], [160, 264])
                    self.assertEqual(set(pose["sockets"]), {"root", "head", "hand_R", "hand_L", "back", "waist"})

    def test_leg_chain_lengths_stay_fixed_through_walk_cycle(self):
        for direction in CANONICAL_DIRECTIONS:
            for frame in range(16):
                pose = swordsman.pose_for(direction, "Walk", frame)
                for side in ("R", "L"):
                    hip = pose["bones"][f"hip_{side}"]
                    knee = pose["bones"][f"knee_{side}"]
                    ankle = pose["bones"][f"ankle_{side}"]
                    femur = math.sqrt(((knee[0]-hip[0])*45)**2 + ((knee[1]-hip[1])*45)**2 + (knee[2]-hip[2])**2)
                    tibia = math.sqrt(((ankle[0]-knee[0])*45)**2 + ((ankle[1]-knee[1])*45)**2 + (ankle[2]-knee[2])**2)
                    self.assertAlmostEqual(femur, 31, places=5)
                    self.assertAlmostEqual(tibia, 29, places=5)

    def test_walk_has_opposed_support_and_visible_swing_clearance(self):
        contact = swordsman.pose_for("S", "Walk", 0)
        passing = swordsman.pose_for("S", "Walk", 4)
        opposite_contact = swordsman.pose_for("S", "Walk", 8)
        self.assertGreater(contact["bones"]["ankle_R"][1], contact["bones"]["ankle_L"][1])
        self.assertGreater(passing["bones"]["ankle_L"][2], 5)
        self.assertGreater(opposite_contact["bones"]["ankle_L"][1], opposite_contact["bones"]["ankle_R"][1])
        vertical_bob = [swordsman.pose_for("S", "Walk", frame)["bob"] for frame in range(16)]
        self.assertGreater(max(vertical_bob) - min(vertical_bob), 3.5)

    def test_each_direction_uses_a_distinct_authored_yaw(self):
        self.assertEqual(len({swordsman.YAW[d] for d in CANONICAL_DIRECTIONS}), 8)


class BakedOutputTests(unittest.TestCase):
    def test_authoring_atlases_match_blueprint_canvas_and_frame_order(self):
        metadata = json.loads((PACKAGE / "authoring-atlases/atlas-metadata.json").read_text())
        self.assertEqual(metadata["directions"], CANONICAL_DIRECTIONS)
        self.assertEqual((metadata["frame"]["width"], metadata["frame"]["height"]), (320, 320))
        self.assertEqual(len(metadata["atlases"]), len(SPEC["authoringLayers"]) * 2)
        for atlas in metadata["atlases"]:
            path = PACKAGE / atlas["file"]
            self.assertTrue(path.is_file(), atlas["file"])
            with path.open("rb") as stream:
                header = stream.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", header[16:24]), (atlas["width"], atlas["height"]))
            self.assertEqual(atlas["height"], 320 * len(CANONICAL_DIRECTIONS))
            expected_count = SPEC["clips"][atlas["clip"]]["frames"]
            self.assertEqual(atlas["width"], 320 * expected_count)
            self.assertEqual(atlas["durationsMs"], SPEC["clips"][atlas["clip"]]["durationsMs"])

    def test_every_cosmetic_swap_only_changes_its_layer_in_all_directions(self):
        report = json.loads((PACKAGE / "review/validation.json").read_text())
        self.assertFalse(report["ownerVisualApproval"])
        self.assertEqual(report["status"], "DEV_ONLY / REQUIRES_OWNER_VISUAL_REVIEW")
        for name, proof in report["cosmeticSwaps"].items():
            self.assertTrue(proof["allDirectionsPass"], name)
            self.assertEqual(list(proof["directions"]), CANONICAL_DIRECTIONS, name)
            for direction, result in proof["directions"].items():
                self.assertTrue(result["onlyExpectedLayersChanged"], f"{name}/{direction}")
                self.assertTrue(result["unchangedLayersEqual"], f"{name}/{direction}")


if __name__ == "__main__":
    unittest.main()
