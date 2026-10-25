import importlib.util
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

MODULE = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/package_visible_pilot_parts.py'
spec = importlib.util.spec_from_file_location('visible_pilot_package', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VisiblePilotPackageTests(unittest.TestCase):
    def fixture(self):
        a = np.zeros((16, 16, 4), 'uint8')
        a[2:14, 2:14] = (175, 70, 30, 255)
        a[2, 2:14] = (220, 130, 70, 83)
        parts = []
        for left, right in [(0, 8), (8, 16)]:
            p = np.zeros_like(a)
            p[:, left:right] = a[:, left:right]
            parts.append(Image.fromarray(p))
        return Image.fromarray(a), parts

    def test_resampled_parts_recompose_exactly(self):
        master, parts = self.fixture()
        target, cutouts = module.normalize(master, parts, 9)
        rebuilt = Image.new('RGBA', target.size)
        for part in cutouts:
            rebuilt.alpha_composite(part)
        self.assertEqual(rebuilt.tobytes(), target.tobytes())

    def test_resampled_ownership_is_exclusive(self):
        master, parts = self.fixture()
        _, cutouts = module.normalize(master, parts, 9)
        coverage = sum((np.array(p)[:, :, 3]>0).astype(int) for p in cutouts)
        self.assertLessEqual(coverage.max(), 1)

    def test_visible_master_pixels_are_not_repainted(self):
        master, parts = self.fixture()
        target, _ = module.normalize(master, parts, 9)
        expected = np.array(master.resize((9, 9), Image.Resampling.LANCZOS))
        actual = np.array(target)
        visible = expected[:, :, 3]>0
        np.testing.assert_array_equal(actual[visible], expected[visible])
        np.testing.assert_array_equal(actual[:, :, 3], expected[:, :, 3])

    def test_incorrect_native_parts_are_rejected(self):
        master, parts = self.fixture()
        parts[0] = Image.new('RGBA', master.size)
        with self.assertRaisesRegex(ValueError, 'Native visible cuts'):
            module.normalize(master, parts, 9)


if __name__ == '__main__':
    unittest.main()
