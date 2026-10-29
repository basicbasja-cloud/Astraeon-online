import sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_pickup_sw08_unmatte as matte
import refine_pickup_sw08_sam_head as head
import refine_pickup_sw08_sam_weapon as weapon
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
MASKS=BASE/'research/swordsman-pickup-sw08-sam-20261029'
class MatteAndSamTests(unittest.TestCase):
 def test_matte_clears_reviewed_gap_and_recomposes(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'matte';r=matte.build(out);im=Image.open(out/'master.png').convert('RGBA');self.assertEqual(im.getpixel((396,542))[3],0);self.assertLessEqual(r['white_recomposite_max_channel_difference'],5)
   combined=Image.new('RGBA',(768,768))
   for role in matte.ORDER:combined.alpha_composite(Image.open(out/'layers'/f'{role}.png').convert('RGBA'))
   self.assertEqual(combined.tobytes(),im.tobytes())
 def test_head_and_weapon_relabels_preserve_master(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);base=BASE/'review/swordsman-pickup-sw08-unmatte-v3-20261029';a=root/'head';b=root/'weapon'
   self.assertTrue(head.build(MASKS/'head/masks/2.png',a,base)['original_keyed_master_exact'])
   self.assertTrue(weapon.build(MASKS/'weapon/masks/2.png',a,b)['same_frame_master_exact'])
   self.assertEqual(Image.open(base/'master.png').convert('RGBA').tobytes(),Image.open(b/'master.png').convert('RGBA').tobytes())
if __name__=='__main__':unittest.main()
