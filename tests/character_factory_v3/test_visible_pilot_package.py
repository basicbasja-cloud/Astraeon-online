import importlib.util
from pathlib import Path
import unittest
import hashlib
import json
import subprocess
import sys
import tempfile

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

    def package_fixture(self, root, frames=32):
        source, masters = root/'cuts', root/'masters'
        source.mkdir()
        masters.mkdir()
        for role in module.ROLES:
            (source/role).mkdir()
        rows = []
        master, halves = self.fixture()
        empty = Image.new('RGBA', master.size)
        for index in range(frames):
            pose = master.copy()
            left_part = halves[0].copy()
            # Distinct pixels exercise real page/rectangle addressing. Only
            # the closing pose intentionally aliases pose zero.
            color = (120+(index if index != frames-1 else 0)%100,70,30,255)
            pose.putpixel((5,5),color)
            left_part.putpixel((5,5),color)
            path = masters/f'{index:03d}.png'
            pose.save(path)
            for role, part in zip(module.ROLES,[left_part,halves[1],empty,empty]):
                part.save(source/role/path.name)
            rows.append({'index':index,'master_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        (source/'receipt.json').write_text(json.dumps({'frames':rows}))
        return source, masters

    def test_32_pose_cycle_uses_two_bounded_pages_and_recomposes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, masters = self.package_fixture(root)
            output = root/'package'
            command = [sys.executable,str(MODULE),'--source',str(source),'--masters',str(masters),
                       '--output',str(output),'--frame-size','16','--loop','--action','CastingCycle']
            subprocess.run(command,check=True,capture_output=True)
            package = json.loads((output/'package.json').read_text())
            self.assertEqual(len(package['frames']),32)
            self.assertEqual(len(package['pages']['Master']),2)
            self.assertEqual(package['sheet_size'],[64,64])
            self.assertTrue(package['loop'])
            for row in package['frames']:
                rebuilt = Image.new('RGBA',(16,16))
                for role in module.ROLES:
                    rebuilt.alpha_composite(Image.open(output/row['files'][role]['path']).convert('RGBA'))
                original = Image.open(output/row['files']['Master']['path']).convert('RGBA')
                self.assertEqual(rebuilt.tobytes(),original.tobytes())
                entry = package['pages']['Master'][row['sheet_page']]
                x,y,w,h = row['sheet_box']
                with Image.open(output/entry['path']) as page:
                    self.assertEqual(page.crop((x,y,x+w,y+h)).tobytes(),original.tobytes())
            with Image.open(output/'cycle-loop.gif') as gif:
                self.assertEqual(gif.info['loop'],0)

    def test_loop_with_different_part_ownership_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, masters = self.package_fixture(root,2)
            Image.new('RGBA',(16,16)).save(source/'HeadHair/001.png')
            result = subprocess.run([sys.executable,str(MODULE),'--source',str(source),'--masters',str(masters),
                       '--output',str(root/'package'),'--frame-size','16','--loop'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Loop part ownership differs',result.stderr)
            self.assertFalse((root/'package').exists())


if __name__ == '__main__':
    unittest.main()
