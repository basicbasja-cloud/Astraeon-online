import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from propose_sword_nw15_alternate_weapon import build,place_sword,BODY,ORDER,compose

class SwordAlternateProposalTests(unittest.TestCase):
 def test_place_requires_square_and_keeps_recorded_canvas(self):
  with self.assertRaisesRegex(ValueError,'square'):place_sword(Image.new('RGBA',(8,7)))
  im=Image.new('RGBA',(150,150));im.putpixel((34,56),(9,18,27,255));result=place_sword(im)
  self.assertEqual(result.size,(768,768));self.assertEqual(result.getpixel((354,486)),(9,18,27,255))
  self.assertEqual(result.getchannel('A').getbbox(),(354,486,355,487))
 def test_one_frame_swap_preserves_nonweapon_and_is_not_approved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'candidate';r=build(out)
   self.assertFalse(r['art_approved']);self.assertFalse(r['runtime_admitted']);self.assertTrue(r['non_weapon_layers_byte_identical'])
   self.assertGreaterEqual(r['alternate_alpha_at_grip'],240);self.assertGreaterEqual(r['hand_alpha_at_grip'],240)
   original={role:np.array(Image.open(BODY/'layers'/f'{role}.png').convert('RGBA')) for role in ORDER}
   changed={role:a.copy() for role,a in original.items()};changed['Weapon']=np.array(Image.open(out/'alternate-weapon.png').convert('RGBA'))
   self.assertEqual(compose(changed).tobytes(),Image.open(out/'master-with-alternate.png').convert('RGBA').tobytes())
   for role in ORDER:
    if role!='Weapon':self.assertTrue(np.array_equal(original[role],changed[role]),role)
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'fresh'):build(Path(tmp))

if __name__=='__main__':unittest.main()
