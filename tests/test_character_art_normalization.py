import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location('normalizer', Path(__file__).resolve().parents[1] / 'tools/normalize_character_art.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        image = Image.new('RGBA', (64, 32))
        draw = ImageDraw.Draw(image)
        for i in range(8):
            x, y = i % 4 * 16, i // 4 * 16
            draw.rectangle((x + 5, y + 4, x + 10, y + 13), fill=(20 * i, 80, 120, 255))
        image.save(self.root / 'art.png')
        self.plan = dict(schemaVersion='1.0', action='Idle', directions=module.DIRECTIONS,
                         canvas=[32,32], root=[16,28], frameCount=1,
                         source=dict(file='art.png', cell=[16,16], root=[8,14], scale=1),
                         frames={d:[dict(column=i%4,row=i//4)] for i,d in enumerate(module.DIRECTIONS)})

    def tearDown(self):
        self.temp.cleanup()

    def test_deterministic_registration_and_export(self):
        a = module.normalize(self.plan, self.root, self.root / 'a')
        b = module.normalize(self.plan, self.root, self.root / 'b')
        self.assertEqual(a, b)
        self.assertEqual((self.root/'a/atlas.png').read_bytes(), (self.root/'b/atlas.png').read_bytes())
        self.assertEqual(len(set(f['pixelSHA256'] for f in a['frames'])), 8)
        self.assertEqual(a['translation'], [8,14])

    def test_clipping_rejects_before_output(self):
        self.plan['source']['scale'] = 10
        with self.assertRaisesRegex(ValueError, 'Clipped'):
            module.normalize(self.plan, self.root, self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_reuse_requires_authored_reason_and_rejects_frame_warp(self):
        self.plan['frameCount'] = 2
        for frames in self.plan['frames'].values():
            frames.append(dict(frames[0]))
        with self.assertRaisesRegex(ValueError, 'reuse'):
            module.normalize(self.plan,self.root,self.root/'out')
        for frames in self.plan['frames'].values():
            frames[1]['reuseReason'] = 'Explicit static standing hold'
        module.normalize(self.plan,self.root,self.root/'out')
        self.plan['frames']['S'][0]['scale'] = .5
        with self.assertRaisesRegex(ValueError, 'transforms'):
            module.normalize(self.plan,self.root,self.root/'bad')

    def test_missing_directions_and_private_reference_rejected(self):
        self.plan['source']['file'] = 'authoring/characters/private-ro-reference/copied.png'
        with self.assertRaisesRegex(ValueError, 'original'):
            module.normalize(self.plan,self.root,self.root/'out')
        self.plan['source']['file'] = 'art.png'
        del self.plan['frames']['NE']
        with self.assertRaisesRegex(ValueError, 'direction'):
            module.normalize(self.plan,self.root,self.root/'out')

    def test_direction_origins_are_fixed_across_frames(self):
        self.plan['frameCount'] = 2
        self.plan['source']['directionRoots'] = {d:[8,13+i%2] for i,d in enumerate(module.DIRECTIONS)}
        for frames in self.plan['frames'].values():
            frames.append(dict(frames[0], reuseReason='Static standing hold'))
        receipt = module.normalize(self.plan, self.root, self.root/'out')
        for i,d in enumerate(module.DIRECTIONS):
            first, second = receipt['frames'][i*2:i*2+2]
            self.assertEqual(first['translation'], [8,15-i%2])
            self.assertEqual(first['translation'], second['translation'])
            self.assertEqual(first['pixelSHA256'], second['pixelSHA256'])
        del self.plan['source']['directionRoots']['NE']
        with self.assertRaisesRegex(ValueError, 'direction origin'):
            module.normalize(self.plan, self.root, self.root/'bad')


if __name__ == '__main__':
    unittest.main()
