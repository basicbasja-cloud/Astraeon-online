import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_factory_v3'))
from audit_bound_cutout_objects import audit


class BoundObjectAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / 'factory'
        (self.base / 'cutout-store').mkdir(parents=True)
        (self.base / 'cutouts/job').mkdir(parents=True)
        self.image = Image.new('RGBA', (2, 2), (1, 2, 3, 255))
        self.digest = hashlib.sha256(self.image.tobytes()).hexdigest()
        self.image.save(self.root / 'part.png')
        self.write('cutout-store/index.json', {'assets': {'a': {'object': self.digest}}, 'objects': {self.digest: {'file': 'part.png', 'canvas': [2, 2], 'rgba_sha256': self.digest}}})
        self.write('cutouts/job/bindings.json', {'frames': [{'assets': {'BodyCostume': 'a'}}]})

    def write(self, name, value):
        (self.base / name).write_text(json.dumps(value))

    def test_intact_pixels_are_not_visual_approval(self):
        result = audit(self.base, self.root)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['objects_read'], 1)
        self.assertFalse(result['art_approved'])

    def test_altered_pixels_are_reported(self):
        Image.new('RGBA', (2, 2), (9, 2, 3, 255)).save(self.root / 'part.png')
        self.assertEqual(audit(self.base, self.root)['errors'][0]['issue'], 'rgba_hash_mismatch')

    def test_outside_path_is_rejected(self):
        self.write('cutout-store/index.json', {'assets': {'a': {'object': self.digest}}, 'objects': {self.digest: {'file': '../outside.png', 'canvas': [2, 2], 'rgba_sha256': self.digest}}})
        self.assertEqual(audit(self.base, self.root)['errors'][0]['issue'], 'object_path_outside_repository')


if __name__ == '__main__':
    unittest.main()
