import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_ranged_visible_cutouts import split_frame


class RangedVisibleCutoutTests(unittest.TestCase):
    def sample(self):
        pixels = np.zeros((32, 32, 4), dtype=np.uint8)
        pixels[3:29, 5:27] = [110, 80, 50, 213]
        annotation = {'head_polygon': [[5, 3], [26, 3], [26, 10], [5, 10]],
                      'weapon_paths': [{'points': [[8, 12], [8, 27]], 'width': 3}],
                      'hand_polygons': [[[5, 17], [12, 17], [12, 21], [5, 21]]]}
        return Image.fromarray(pixels), annotation

    def test_same_frame_partial_alpha_pixels_reconstruct_exactly(self):
        master, annotation = self.sample()
        parts, labels, report = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})
        result = Image.new('RGBA', master.size)
        for role in ['BodyCostume', 'HeadHair', 'Weapon']:
            result.alpha_composite(parts[role])
        self.assertEqual(result.tobytes(), master.tobytes())
        self.assertEqual(report['recomposition_mismatches'], 0)
        self.assertEqual(set(np.unique(labels)), {0, 1, 2, 3})

    def test_visible_hand_stays_with_complete_clothed_body(self):
        master, annotation = self.sample()
        parts, labels, _ = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})
        self.assertEqual(labels.getpixel((8, 19)), 1)
        self.assertEqual(parts['BodyCostume'].getpixel((8, 19)), master.getpixel((8, 19)))
        self.assertEqual(parts['Weapon'].getpixel((8, 19))[3], 0)
        self.assertEqual(labels.getpixel((8, 25)), 3)

    def test_head_exclusion_does_not_erase_master_pixels(self):
        master, annotation = self.sample()
        annotation['head_exclusions'] = [[[5, 5], [10, 5], [10, 8], [5, 8]]]
        parts, labels, _ = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})
        self.assertEqual(labels.getpixel((7, 6)), 1)
        self.assertEqual(parts['BodyCostume'].getpixel((7, 6)), master.getpixel((7, 6)))

    def test_material_profile_requires_real_facial_skin(self):
        master, annotation = self.sample()
        annotation['head_material_profile'] = 'chestnut-archer-v1'
        with self.assertRaisesRegex(ValueError, 'facial skin'):
            split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})

    def test_explicit_foreground_hand_stays_body_when_crossing_head(self):
        master, annotation = self.sample()
        annotation['hands_occlude_head'] = True
        annotation['hand_polygons'].append([[12, 6], [18, 6], [18, 9], [12, 9]])
        parts, labels, report = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})
        self.assertEqual(labels.getpixel((15, 7)), 1)
        self.assertEqual(parts['HeadHair'].getpixel((15, 7))[3], 0)
        self.assertEqual(parts['BodyCostume'].getpixel((15, 7)), master.getpixel((15, 7)))
        self.assertEqual(report['recomposition_mismatches'], 0)

    def test_external_head_must_preserve_the_same_source_pixels(self):
        master, annotation = self.sample()
        head = master.copy()
        head.putpixel((8, 8), (255, 0, 255, 255))
        with self.assertRaisesRegex(ValueError, 'same master pixels'):
            split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]}, head)

    def test_external_head_keeps_its_partial_alpha(self):
        master, annotation = self.sample()
        head = Image.new('RGBA', master.size)
        head.putpixel((8, 8), master.getpixel((8, 8)))
        parts, labels, report = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]}, head)
        self.assertEqual(parts['HeadHair'].tobytes(), head.tobytes())
        self.assertEqual(labels.getpixel((8, 8)), 2)
        self.assertEqual(report['recomposition_mismatches'], 0)

    def test_visible_boundary_clip_changes_ownership_not_master_pixels(self):
        master, annotation = self.sample()
        annotation['head_clip_polygon'] = [[5, 3], [15, 3], [15, 10], [5, 10]]
        parts, labels, report = split_frame(master, annotation, {'scale': 1, 'offset': [0, 0]})
        self.assertEqual(labels.getpixel((8, 7)), 2)
        self.assertEqual(labels.getpixel((20, 7)), 1)
        self.assertEqual(parts['BodyCostume'].getpixel((20, 7)), master.getpixel((20, 7)))
        self.assertEqual(report['recomposition_mismatches'], 0)


if __name__ == '__main__':
    unittest.main()
