import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'))
import audit_swordsman_walk_sw_loop as audit

class WalkLoopAuditTest(unittest.TestCase):
 def test_fixed_sheet_yields_sixteen_frames(self):
  tiles = audit.read_tiles(audit.SOURCE / 'generated-sheet.png')
  self.assertEqual(len(tiles), 16)
  self.assertTrue(all(frame.size == (384, 384) for frame in tiles))

 def test_identical_frame_has_zero_difference(self):
  im = Image.new('RGB', (4, 4), 'black')
  self.assertEqual(audit.difference(im, im), (0.0, 16))

 def test_refuses_to_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):
    audit.build(Path(tmp))

if __name__ == '__main__': unittest.main()
