import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/character_factory_v3'))
from audit_frame_coverage import audit


class FrameCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.write('factory.json', {'characters': [{'id': 'p', 'class': 'c'}], 'classes': {'c': {'actions': {'Attack': {'frames': 1, 'authored_directions': ['SW'], 'loop': False}}}}})
        self.write('ledger.json', {'action_guide_bindings': {'c/Attack': 'g'}, 'paint_jobs': {'j': {'id': 'j', 'character': 'p', 'actions': ['Attack'], 'guide_job': 'g', 'frame_count': 1}}})
        self.write('cutout-store/index.json', {'assets': {}, 'objects': {}})
        guide = self.base / 'guides/g/SW/000.png'
        guide.parent.mkdir(parents=True)
        guide.write_bytes(b'present only')

    def write(self, name, data):
        path = self.base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def test_guide_does_not_mean_import_or_approval(self):
        row = audit(self.base)['rows'][0]
        self.assertTrue(row['guide_png_present'])
        self.assertFalse(row['binding_present'])
        self.assertFalse(row['technical_import_receipt'])
        self.assertFalse(row['visual_approved'])
        self.assertFalse(row['runtime_approved'])

    def test_missing_assets_are_reported(self):
        self.write('cutouts/j/bindings.json', {'paint_job': 'j', 'frames': [{'direction': 'SW', 'index': 0, 'assets': {}}]})
        row = audit(self.base)['rows'][0]
        self.assertTrue(row['binding_present'])
        self.assertIn('Weapon:missing_asset', row['core_metadata_issues'])

    def test_duplicate_frame_binding_rejected(self):
        frame = {'direction': 'SW', 'index': 0, 'assets': {}}
        self.write('cutouts/j/bindings.json', {'paint_job': 'j', 'frames': [frame, frame]})
        with self.assertRaisesRegex(ValueError, 'Duplicate frame binding'):
            audit(self.base)


if __name__ == '__main__':
    unittest.main()
