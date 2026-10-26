import sys
import json
import tempfile
from unittest.mock import patch
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_ranged_visible_cutouts import split_frame, sequence_layout, main


class RangedVisibleCutoutTests(unittest.TestCase):
    def test_twenty_four_pose_parts_cannot_clip_after_frame_fifteen(self):
        self.assertEqual(sequence_layout([{'index': i} for i in range(24)]), (2048, 3072))

    def test_sixteen_pose_sheet_dimensions_remain_unchanged(self):
        self.assertEqual(sequence_layout([{'index': i} for i in range(16)]), (2048, 2048))

    def test_duplicate_or_missing_frame_annotations_fail(self):
        for items in [[], [{'index': 0}, {'index': 0}], [{'index': 0}, {'index': 2}]]:
            with self.assertRaisesRegex(ValueError, 'contiguous'):
                sequence_layout(items)

    def test_export_retains_last_of_twenty_four_frames(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frames = root/'frames'; frames.mkdir()
            items = []
            for index in range(24):
                image = Image.new('RGBA', (512, 512))
                image.putpixel((100, 100), (120, 70, 30, 254))
                image.save(frames/f'{index:03d}.png')
                items.append({'index': index, 'head_polygon': [[95, 95], [105, 95], [105, 105], [95, 105]],
                              'weapon_paths': [], 'hand_polygons': []})
            annotations = root/'annotations.json'
            annotations.write_text(json.dumps({'frames': items, 'cell_to_frame': {'scale': 1, 'offset': [0, 0]}}))
            output = root/'output'
            with patch.object(sys, 'argv', ['cutouts', '--frames', str(frames), '--annotations', str(annotations), '--output', str(output)]):
                main()
            with Image.open(output/'HeadHair-sheet.png') as sheet:
                self.assertEqual(sheet.size, (2048, 3072))
                self.assertEqual(sheet.getpixel((3*512+100, 5*512+100)), (120, 70, 30, 254))
            self.assertTrue((output/'HeadHair/023.png').is_file())

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
