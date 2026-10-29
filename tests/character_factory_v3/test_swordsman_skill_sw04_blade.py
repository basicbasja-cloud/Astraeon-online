import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_skill_sw04_blade as tool
class SkillBladeTest(unittest.TestCase):
 def test_changes_only_where_mask_nonzero(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'result';receipt=tool.build(out)
   a=np.asarray(Image.open(out/'initial.png'));b=np.asarray(Image.open(out/'candidate.png'));mask=np.asarray(Image.open(out/'mask.png'))
   self.assertGreater(receipt['changed_pixels'],0)
   self.assertFalse(np.any(np.any(a!=b,axis=2)&(mask==0)))
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):tool.build(Path(d))
if __name__=='__main__':unittest.main()
