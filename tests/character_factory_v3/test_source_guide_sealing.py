import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, PngImagePlugin

SCRIPT = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/seal_source_guide_replay.py'
spec = importlib.util.spec_from_file_location('guide_sealing', SCRIPT)
sealing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sealing)


class SourceGuideSealingTests(unittest.TestCase):
    def source(self, folder, date):
        (folder / 'SW').mkdir(parents=True)
        for index in range(2):
            image = Image.new('RGBA', (2, 2), (23, 41, 77, 0))
            image.putpixel((1, 0), (213, 100, 80, 111))
            info = PngImagePlugin.PngInfo()
            info.add_text('Date', date)
            image.save(folder / 'SW' / f'{index:03}.png', pnginfo=info)
        manifest = {'frame_count': 2, 'job': {'resolution': 2, 'directions': ['SW'], 'source_sha256': 'fixture'},
                    'views': {'SW': {'frames': [{'frame': i, 'image': f'SW/{i:03}.png'} for i in range(2)]}}}
        (folder / 'manifest.json').write_text(json.dumps(manifest))

    def test_volatile_metadata_is_removed_without_changing_hidden_rgb_or_partial_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.source(root / 'a', 'first render')
            self.source(root / 'b', 'second render')
            sealing.seal(root / 'a', root / 'sealed-a')
            sealing.seal(root / 'b', root / 'sealed-b')
            self.assertNotEqual((root / 'a/SW/000.png').read_bytes(), (root / 'b/SW/000.png').read_bytes())
            for path in (root / 'sealed-a').rglob('*'):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (root / 'sealed-b' / path.relative_to(root / 'sealed-a')).read_bytes())
            with Image.open(root / 'sealed-a/SW/000.png') as image:
                self.assertEqual(image.getpixel((0, 0)), (23, 41, 77, 0))
                self.assertEqual(image.getpixel((1, 0)), (213, 100, 80, 111))
            with self.assertRaisesRegex(ValueError, 'fresh output'):
                sealing.seal(root / 'a', root / 'sealed-a')

    def test_late_missing_source_frame_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.source(root / 'a', 'render')
            (root / 'a/SW/001.png').unlink()
            with self.assertRaises(FileNotFoundError):
                sealing.seal(root / 'a', root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_failure_after_first_packaged_frame_removes_only_owned_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.source(root / 'a', 'render')
            original = (root / 'a/SW/000.png').read_bytes()
            sibling = root / 'preserve.txt'
            sibling.write_text('prior work')
            normalize = sealing.normalize_png
            calls = []

            def fail_second(path):
                calls.append(path)
                if len(calls) == 2:
                    raise OSError('simulated disk write preparation failure')
                return normalize(path)

            with patch.object(sealing, 'normalize_png', side_effect=fail_second):
                with self.assertRaises(OSError):
                    sealing.seal(root / 'a', root / 'out')
            self.assertFalse((root / 'out').exists())
            self.assertEqual((root / 'a/SW/000.png').read_bytes(), original)
            self.assertEqual(sibling.read_text(), 'prior work')


if __name__ == '__main__':
    unittest.main()
