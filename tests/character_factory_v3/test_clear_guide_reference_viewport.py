import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from prepare_clear_guide_batches import checked_viewport


class ClearGuideViewportTests(unittest.TestCase):
    def test_all_poses_have_margin(self):
        self.assertEqual(checked_viewport([[3,3,8,8],[4,3,9,9]],[2,2,10,10],(12,12)),1)

    def test_later_pose_foot_is_not_silently_cut(self):
        with self.assertRaisesRegex(ValueError,'clips or touches'):
            checked_viewport([[3,3,8,8],[3,3,8,11]],[2,2,10,10],(12,12))

    def test_weapon_on_reference_edge_is_rejected(self):
        with self.assertRaises(ValueError):checked_viewport([[2,3,8,8]],[2,2,10,10],(12,12))

    def test_rectangular_crop_cannot_be_stretched_to_square(self):
        with self.assertRaisesRegex(ValueError,'square'):checked_viewport([[3,3,8,8]],[2,2,10,11],(12,12))

    def test_source_overscan_must_exist(self):
        with self.assertRaisesRegex(ValueError,'overscan'):checked_viewport([[3,3,8,8]],[-1,-1,11,11],(12,12))

    def test_empty_source_and_boolean_coordinates_fail(self):
        for boxes,viewport in [([],[2,2,10,10]),([[3,3,8,8]],[True,2,10,10])]:
            with self.assertRaises(ValueError):checked_viewport(boxes,viewport,(12,12))
