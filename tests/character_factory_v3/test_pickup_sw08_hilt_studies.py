import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import refine_pickup_sw08_weapon_debris as debris
import propose_pickup_sw08_hilt_underpaint as underpaint
class HiltStudiesTests(unittest.TestCase):
 def test_debris_relabels_without_changing_master(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'out';r=debris.build(out);self.assertEqual(r['transferred_pixels'],9);self.assertEqual(Image.open(out/'master.png').convert('RGBA').tobytes(),Image.open(debris.BASE/'master.png').convert('RGBA').tobytes())
 def test_underpaint_is_fully_covered_and_same_composite(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'out';r=underpaint.build(out);m=np.array(Image.open(out/'underpaint-mask.png'))>0;w=np.array(Image.open(underpaint.BASE/'layers/Weapon.png').convert('RGBA'));self.assertTrue(m.any());self.assertTrue(np.all(w[:,:,3][m]==255));self.assertTrue(r['original_sword_on_master_exact'])
   im=Image.new('RGBA',(768,768))
   for role in underpaint.ORDER:im.alpha_composite(Image.open(out/'layers'/f'{role}.png').convert('RGBA'))
   self.assertEqual(im.tobytes(),Image.open(out/'master.png').convert('RGBA').tobytes())
 def test_closed_fist_donor_stays_under_opaque_weapon(self):
  donor=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-hilt-fist-20261029/donor.png'
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'fist';r=underpaint.build(out,donor);mask=np.array(Image.open(out/'underpaint-mask.png'))>0;w=np.array(Image.open(underpaint.BASE/'layers/Weapon.png').convert('RGBA'));self.assertGreater(r['inserted_pixels'],0);self.assertTrue(np.all(w[:,:,3][mask]==255));self.assertTrue(r['original_sword_on_master_exact'])
if __name__=='__main__':unittest.main()
