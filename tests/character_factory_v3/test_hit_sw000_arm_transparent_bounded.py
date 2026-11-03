import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_hit_sw000_arm_transparent_bounded as study
class ArmPatchTests(unittest.TestCase):
 def test_unchanged_outside_and_alpha_coverage(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'candidate';proof=study.build(out);self.assertEqual(proof['outside_mask_difference'],0)
   before=np.asarray(Image.open(study.BASE).convert('RGBA'));after=np.asarray(Image.open(out/'candidate.png').convert('RGBA'));mask=np.asarray(Image.open(out/'mask.png'))>0
   np.testing.assert_array_equal(before[~mask],after[~mask]);self.assertTrue(np.any(before[mask]!=after[mask]));self.assertTrue(np.any(after[mask,3]<255))
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
