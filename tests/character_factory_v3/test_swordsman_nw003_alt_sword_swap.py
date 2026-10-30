import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_nw003_alt_sword_swap as study
class AlternateSwordTests(unittest.TestCase):
 def test_outside_swap_union_is_unchanged(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'result';receipt=study.build(out)
   self.assertEqual(receipt['changed_outside_swap_union'],0)
   original=np.asarray(Image.open(study.UNDER).convert('RGBA'));result=np.asarray(Image.open(out/'alternate-composite.png').convert('RGBA'))
   sword=np.asarray(Image.open(out/'alternate-weapon.png').convert('RGBA'))[:,:,3]>0
   hand=np.asarray(Image.open(out/'hand-occluder.png').convert('RGBA'))[:,:,3]>0
   np.testing.assert_array_equal(original[~(sword|hand)],result[~(sword|hand)])
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
