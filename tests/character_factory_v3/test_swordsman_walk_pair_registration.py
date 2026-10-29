import sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_walk_pair_registration as r
import build_swordsman_walk_pair_guide as g
class WalkPairTests(unittest.TestCase):
 def test_translation_preserves_pixel_and_rejects_clipping(self):
  im=Image.new('RGB',(20,20),'white');im.putpixel((10,10),(0,0,0));self.assertEqual(r.translate(im,(2,-1)).getpixel((12,9)),(0,0,0))
  with self.assertRaises(ValueError):r.translate(im,(11,0))
 def test_bad_pair_start_and_existing_output_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):g.build(3,Path(d)/'x.png')
   with self.assertRaises(ValueError):r.make(Path(d))
if __name__=='__main__':unittest.main()
