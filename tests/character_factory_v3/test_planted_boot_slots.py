import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np
from PIL import Image


MODULE = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/reuse_planted_boots_pilot.py'
spec = importlib.util.spec_from_file_location('boot_slots', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlantedBootSlotTests(unittest.TestCase):
    def test_identity_preserves_exact_rgba(self):
        a = np.zeros((8, 8, 4), 'uint8')
        a[2:6, 2:6] = (180, 90, 30, 137)
        image = Image.fromarray(a)
        result = module.rigid_slot(image, [3, 4], [3, 4], 0)
        self.assertEqual(result.tobytes(), image.tobytes())

    def test_socket_translation_places_actual_pixel(self):
        image = Image.new('RGBA', (12, 12))
        image.putpixel((3, 4), (200, 80, 30, 255))
        result = module.rigid_slot(image, [3, 4], [7, 6], 0)
        self.assertEqual(result.getpixel((7, 6)), (200, 80, 30, 255))
        self.assertEqual(result.getpixel((3, 4))[3], 0)

    def test_rotation_uses_socket_and_screen_coordinate_direction(self):
        image = Image.new('RGBA', (12, 12))
        image.putpixel((6, 5), (200, 80, 30, 255))
        # Camera projections use continuous canvas coordinates; the center of
        # pixel (5, 5) is (5.5, 5.5).
        result = module.rigid_slot(image, [5.5, 5.5], [5.5, 5.5], math.pi / 2)
        self.assertEqual(result.getpixel((5, 6)), (200, 80, 30, 255))

    def test_fractional_transform_uses_premultiplied_edges(self):
        image = Image.new('RGBA', (16, 16))
        for x in range(5, 10):
            for y in range(5, 10):
                image.putpixel((x, y), (220, 100, 40, 255))
        result = np.array(module.rigid_slot(image, [7, 7], [7.5, 7.25], 0))
        visible = result[:, :, 3] > 32
        self.assertTrue(visible.any())
        self.assertLessEqual(np.max(abs(result[visible, :3].astype(int)-[220, 100, 40])), 5)

    def test_toe_direction_is_anatomical_side_specific(self):
        landmarks = {'Foot.L': [3, 3], 'Toe.L': [2, 3], 'Foot.R': [6, 3], 'Toe.R': [6, 2]}
        self.assertAlmostEqual(module.angle(landmarks, 'L'), math.pi)
        self.assertAlmostEqual(module.angle(landmarks, 'R'), -math.pi / 2)


if __name__ == '__main__':
    unittest.main()
