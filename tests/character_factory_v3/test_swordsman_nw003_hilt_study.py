import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_nw003_hilt_study as study
class HiltStudyTests(unittest.TestCase):
 def test_exact_reconstruction_and_outside_mask(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'result';receipt=study.build(out)
   self.assertEqual(receipt['rgba_difference_pixels'],0)
   with Image.open(study.base.SOURCE/'Master/003.png') as im:master=np.asarray(im.convert('RGBA'))
   result=np.asarray(Image.open(out/'recomposed.png').convert('RGBA'));np.testing.assert_array_equal(master,result)
   under=np.asarray(Image.open(out/'underpaint-no-blade.png').convert('RGBA'));mask=np.asarray(Image.open(out/'blade-mask.png'))>0
   np.testing.assert_array_equal(master[~mask],under[~mask])
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
