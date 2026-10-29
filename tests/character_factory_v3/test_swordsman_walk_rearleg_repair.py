import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_walk_rearleg_repair as p
class RearlegRepairTests(unittest.TestCase):
 def test_outside_mask_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'candidate';r=p.build(out)
   a=np.asarray(Image.open(out/'source.png'));b=np.asarray(Image.open(out/'candidate.png'));m=np.asarray(Image.open(out/'mask.png'))
   self.assertGreater(r['changed_pixels'],0);self.assertFalse(np.any(np.any(a!=b,axis=2)&(m==0)))
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):p.build(Path(d))
if __name__=='__main__':unittest.main()
