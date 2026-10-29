import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_walk_sw02_sole_crop as p
class SW02SoleCropTests(unittest.TestCase):
 def test_outputs_preserve_outside_mask(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'out';proof=p.build(out);a=np.asarray(Image.open(out/'source.png'));m=np.asarray(Image.open(out/'mask.png'))
   for name in ('v1','v2'):
    b=np.asarray(Image.open(out/f'{name}.png'));self.assertFalse(np.any(np.any(a!=b,axis=2)&(m==0)))
   self.assertEqual(proof['status'],'BOUNDED_SW02_REPAINT_PROPOSALS_NOT_APPROVED')
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):p.build(Path(d))
if __name__=='__main__':unittest.main()
