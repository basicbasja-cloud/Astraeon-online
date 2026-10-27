import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image

PATH = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/replay_visible_ownership_study.py'
SPEC = importlib.util.spec_from_file_location('visible_ownership_study_replay', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VisibleStudyReplayTest(unittest.TestCase):
    def setUp(self):
        self.master = Image.fromarray(np.array([[[100, 50, 20, 128], [80, 60, 20, 255], [9, 8, 7, 0]]], dtype='uint8'))
        self.labels = Image.fromarray(np.array([[1, 2, 0]], dtype='uint8'))
        self.roles = {'1': 'BodyRest', '2': 'HeadHair'}

    def test_exact_visible_pixels_keep_explicit_bodyrest_role(self):
        parts = MODULE.split(self.master, self.labels, self.roles)
        self.assertEqual(set(parts), {'BodyRest', 'HeadHair'})
        self.assertEqual(parts['BodyRest'].getpixel((0, 0)), (100, 50, 20, 128))
        self.assertEqual(parts['HeadHair'].getpixel((1, 0)), (80, 60, 20, 255))

    def test_missing_visible_owner_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Every visible'):
            MODULE.split(self.master, Image.fromarray(np.array([[0, 2, 0]], dtype='uint8')), self.roles)

    def test_bodyrest_cannot_be_silently_called_bodycostume(self):
        with self.assertRaisesRegex(ValueError, 'Invalid explicit'):
            MODULE.split(self.master, self.labels, {'1': 'BodyCostume', '2': 'HeadHair'})

    def recipe(self, root):
        master, labels = root / 'master.png', root / 'labels.png'
        self.master.save(master)
        self.labels.save(labels)
        parts = MODULE.split(self.master, self.labels, self.roles)
        data = {'schema': MODULE.SCHEMA, 'runtime_admitted': False, 'role_ids': self.roles,
                'frames': [{'id': 'female/SW/000', 'master': str(master), 'master_sha256': MODULE.sha(master),
                            'labels': str(labels), 'labels_sha256': MODULE.sha(labels),
                            'part_rgba_sha256': {r: hashlib.sha256(p.tobytes()).hexdigest() for r, p in parts.items()}}]}
        path = root / 'recipe.json'
        path.write_text(json.dumps(data))
        return path

    def test_fresh_replay_requires_no_generation_and_preserves_native_canvas(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = MODULE.replay(self.recipe(root), root / 'output')
            self.assertEqual(result['frames'], 1)
            self.assertEqual(len(result['role_checks']), 2)
            self.assertFalse(result['runtime_admitted'])
            self.assertTrue(result['BodyRest_contains_unseparated_weapon'])
            with Image.open(root / 'output/female/SW/000/HeadHair.png') as image:
                self.assertEqual(image.size, (3, 1))

    def test_changed_input_rejected_before_output_written(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            recipe = self.recipe(root)
            (root / 'labels.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Pinned study input changed'):
                MODULE.replay(recipe, root / 'output')
            self.assertFalse((root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
