import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'))
from propose_swordsman_interpolated_sweep import mapped_path
from build_long_sweep_sword_trail import bounded_path, path_length

class SweepStudyTests(unittest.TestCase):
    def setUp(self):
        self.samples = [{'grip': [i, 0], 'tip': [i + 10, 0]} for i in range(65)]
        self.annotations = [{'weapon_grip': [k * 16 + 3, 4], 'weapon_tip': [k * 16 + 13, 4]} for k in range(5)]

    def test_key_registration_and_intermediate_path(self):
        path, _ = mapped_path(self.samples, self.annotations)
        for i, (grip, tip) in enumerate(path):
            np.testing.assert_allclose(grip, [i + 3, 4], atol=1e-7)
            np.testing.assert_allclose(tip, [i + 13, 4], atol=1e-7)

    def test_invalid_sample_count_or_blade_rejected(self):
        with self.assertRaises(ValueError):
            mapped_path(self.samples[:-1], self.annotations)
        self.samples[0]['tip'] = self.samples[0]['grip']
        with self.assertRaises(ValueError):
            mapped_path(self.samples, self.annotations)

    def test_history_is_bounded_and_ends_at_current_sample(self):
        path, _ = mapped_path(self.samples, self.annotations)
        history = bounded_path(path[:49], 25)
        self.assertLessEqual(path_length(history), 25.00001)
        np.testing.assert_allclose(history[-1][1], path[48][1])

if __name__ == '__main__':
    unittest.main()
