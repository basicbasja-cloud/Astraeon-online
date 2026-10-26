import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from propose_sequence_head_cutouts import respects_head_points


class HeadPromptConstraintTests(unittest.TestCase):
    def test_mask_must_include_head_and_exclude_body(self):
        mask = np.zeros((8, 8), dtype=bool)
        mask[2:5, 2:5] = True
        self.assertTrue(respects_head_points(mask, [[3, 3], [6, 6]], 1))

    def test_high_scoring_mask_cannot_include_negative_hand(self):
        mask = np.ones((8, 8), dtype=bool)
        self.assertFalse(respects_head_points(mask, [[3, 3], [6, 6]], 1))

    def test_missing_positive_face_is_rejected(self):
        mask = np.zeros((8, 8), dtype=bool)
        mask[3, 3] = True
        self.assertFalse(respects_head_points(mask, [[3, 3], [4, 4], [6, 6]], 2))

    def test_outside_point_is_not_clamped_onto_another_body_pixel(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            respects_head_points(np.ones((8, 8), dtype=bool), [[8, 4]], 1)


if __name__ == '__main__':
    unittest.main()
