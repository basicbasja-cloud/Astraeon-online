import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_hit_sw000_transparent_mask_patch as study
class HitMaskPatchTests(unittest.TestCase):
 def test_fixed_canvas_outside_mask_and_alpha_change_record(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'result';receipt=study.build(out)
   original=np.asarray(Image.open(study.BASE).convert('RGBA'));candidate=np.asarray(Image.open(out/'candidate.png').convert('RGBA'));mask=np.asarray(Image.open(out/'mask.png'))>0
   np.testing.assert_array_equal(original[~mask],candidate[~mask]);self.assertEqual(receipt['opaque_to_transparent_pixels'],int(((original[:,:,3]>=240)&(candidate[:,:,3]<10)).sum()))
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
