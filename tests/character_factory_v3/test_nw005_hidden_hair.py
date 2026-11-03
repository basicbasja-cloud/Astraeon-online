import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_nw005_hidden_hair as study
class HiddenHairTests(unittest.TestCase):
 def test_underpaint_only_beneath_opaque_weapon_and_recomposes(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'result';proof=study.build(out);self.assertGreater(proof['underpaint_pixels'],0);self.assertEqual(proof['visible_recomposition_mismatches'],0)
   mask=np.asarray(Image.open(out/'underpaint-mask.png').convert('L'))>0;weapon=np.asarray(Image.open(study.O/'Weapon.png').convert('RGBA'));self.assertTrue(np.all(weapon[:,:,3][mask]==255))
   original=np.asarray(Image.open(study.O/'HeadHair.png').convert('RGBA'));head=np.asarray(Image.open(out/'HeadHair-underpaint.png').convert('RGBA'));np.testing.assert_array_equal(original[~mask],head[~mask]);np.testing.assert_array_equal(np.asarray(Image.open(study.SRC/'Master/005.png').convert('RGBA')),np.asarray(Image.open(out/'recomposed.png').convert('RGBA')))
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
