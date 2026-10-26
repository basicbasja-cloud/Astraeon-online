import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from register_planted_foot_masters import observed_sole, rigid_translation, source_foot_ranges, paired_sole_evidence


class PlantedFootRegistrationTests(unittest.TestCase):
    def image(self):
        a = np.zeros((64, 64, 4), dtype=np.uint8)
        a[20:55, 20:40] = [120, 80, 40, 254]
        a[15:59, 48:51] = [70, 40, 20, 254]  # A lower staff shaft.
        return Image.fromarray(a)

    def test_narrow_staff_is_not_the_support_sole(self):
        sole, _ = observed_sole(self.image())
        np.testing.assert_array_equal(sole, [29.5, 54])

    def test_translation_keeps_all_rgba_pixels(self):
        source = self.image()
        translated = rigid_translation(source, np.array([-4, -3]))
        restored = rigid_translation(translated, np.array([4, 3]))
        self.assertEqual(source.tobytes(), restored.tobytes())

    def test_walk_source_cannot_be_treated_as_a_planted_cast(self):
        rows = [{'landmarks': {'foot_l': [0, 0], 'foot_r': [5, 5]}},
                {'landmarks': {'foot_l': [20, 0], 'foot_r': [5, 5]}}]
        with self.assertRaisesRegex(ValueError, 'not sufficiently planted'):
            source_foot_ranges(rows)

    def test_one_stable_foot_does_not_hide_other_foot_drift(self):
        first = [{'point': [10, 50]}, {'point': [40, 50]}]
        current = [{'point': [15, 55]}, {'point': [52, 55]}]
        self.assertEqual(paired_sole_evidence(first, current, [-5, -5])['status'],
                         'BLOCKED_NONRIGID_FOOT_DRIFT')

    def test_rigid_pair_passes_regardless_of_component_order(self):
        first = [{'point': [10, 50]}, {'point': [40, 50]}]
        current = [{'point': [45, 55]}, {'point': [15, 55]}]
        self.assertEqual(paired_sole_evidence(first, current, [-5, -5])['status'],
                         'PASS_TWO_VISIBLE_SOLES')

    def test_merged_feet_require_reviewed_association(self):
        self.assertEqual(paired_sole_evidence([{'point': [10, 50]}], [], [0, 0])['status'],
                         'BLOCKED_AMBIGUOUS_BOOT_ASSOCIATION')

    def test_registration_refuses_clipping(self):
        with self.assertRaisesRegex(ValueError, 'clip'):
            rigid_translation(self.image(), np.array([40, 0]))


if __name__ == '__main__':
    unittest.main()
