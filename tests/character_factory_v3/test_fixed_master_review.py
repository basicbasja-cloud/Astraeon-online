import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from render_fixed_master_review import render


class FixedMasterReviewTests(unittest.TestCase):
    def recipe(self):
        return {'source_size': [16, 16], 'viewport': [0, 0, 16, 16],
                'frame_count': 2, 'sample_ms': 80, 'terminal_hold_ms': 240,
                'identities': ['sample'], 'directions': ['NW'], 'contact_indices': [0, 1]}

    def test_shared_viewport_keeps_sources_immutable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root/'input/sample/NW/Master'
            folder.mkdir(parents=True)
            for index in range(2):
                Image.new('RGBA', (16, 16), (index*100, 80, 50, 213)).save(folder/f'{index:03d}.png')
            originals = [path.read_bytes() for path in sorted(folder.glob('*.png'))]
            receipt = render(root/'input', self.recipe(), root/'output')
            self.assertEqual(len(receipt['frames']), 2)
            self.assertEqual(originals, [path.read_bytes() for path in sorted(folder.glob('*.png'))])
            self.assertFalse(receipt['source_pixels_moved_or_fitted'])

    def test_invalid_viewport_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            recipe = self.recipe()
            recipe['viewport'] = [0, 0, 17, 16]
            with self.assertRaisesRegex(ValueError, 'outside'):
                render(root, recipe, root/'output')
            self.assertFalse((root/'output').exists())


if __name__ == '__main__':
    unittest.main()
