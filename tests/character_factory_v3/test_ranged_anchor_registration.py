import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from register_annotated_ranged_study import anchor_translation


class RangedAnchorRegistrationTests(unittest.TestCase):
    def test_legacy_ankle_coordinates_are_unchanged(self):
        observed, target, delta = anchor_translation(
            {'ankle': [10, 20]},
            {'paint_cell_scale': 2, 'paint_cell_offset': [5, 7]},
            {'landmarks': {'foot_l': [100, 120]}})
        np.testing.assert_array_equal(observed, [25, 47])
        np.testing.assert_array_equal(target, [50, 60])
        np.testing.assert_array_equal(delta, [25, 13])

    def test_explicit_pelvis_does_not_read_ankles(self):
        observed, target, delta = anchor_translation(
            {'pelvis': [100, 120]},
            {'observed_anchor': 'pelvis', 'source_anchor': 'pelvis',
             'paint_cell_scale': 1, 'paint_cell_offset': [99, 80],
             'source_projection_scale': .5},
            {'landmarks': {'pelvis': [800, 900]}})
        np.testing.assert_array_equal(delta, [201, 250])
        self.assertLessEqual(np.linalg.norm(observed+delta-target), 2**-.5)

    def test_missing_landmark_fails_instead_of_falling_back(self):
        with self.assertRaises(KeyError):
            anchor_translation({'pelvis': [1, 2]},
                {'observed_anchor': 'pelvis', 'source_anchor': 'pelvis',
                 'paint_cell_scale': 1, 'paint_cell_offset': [0, 0]},
                {'landmarks': {'foot_l': [3, 4]}})

    def test_nonfinite_coordinates_fail(self):
        with self.assertRaisesRegex(ValueError, 'finite'):
            anchor_translation({'ankle': [float('nan'), 2]},
                {'paint_cell_scale': 1, 'paint_cell_offset': [0, 0]},
                {'landmarks': {'foot_l': [3, 4]}})


if __name__ == '__main__':
    unittest.main()
