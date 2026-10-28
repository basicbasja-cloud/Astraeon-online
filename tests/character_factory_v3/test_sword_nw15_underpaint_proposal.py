import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from propose_sword_nw15_underpaint_v3 import build, select_underpaint, V2, ORDER, compose

class SwordUnderpaintProposalTests(unittest.TestCase):
 def test_selection_requires_opaque_weapon_and_empty_body_and_hand(self):
  body=np.zeros((1,6,4),dtype=np.uint8);weapon=np.zeros_like(body);hand=np.zeros_like(body);donor=np.zeros_like(body);mask=np.ones((1,6),bool)
  weapon[:,:,3]=255;donor[:,:,3]=255
  weapon[0,1,3]=254;body[0,2,3]=1;hand[0,3,3]=1;donor[0,4,3]=239;mask[0,5]=False
  self.assertEqual(select_underpaint(body,weapon,hand,donor,mask).tolist(),[[True,False,False,False,False,False]])
 def test_replay_changes_only_protected_body_pixels_and_not_master(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'candidate';report=build(out)
   self.assertGreater(report['underpaint_pixels'],0);self.assertTrue(report['previous_master_byte_exact']);self.assertFalse(report['art_approved']);self.assertFalse(report['runtime_admitted'])
   original={r:np.array(Image.open(V2/'layers'/f'{r}.png').convert('RGBA')) for r in ORDER};new={r:np.array(Image.open(out/'layers'/f'{r}.png').convert('RGBA')) for r in ORDER}
   changed=np.any(original['BodyCostume']!=new['BodyCostume'],axis=2)
   self.assertEqual(int(changed.sum()),report['underpaint_pixels'])
   self.assertTrue(np.all(original['BodyCostume'][:,:,3][changed]==0))
   self.assertTrue(np.all(original['Weapon'][:,:,3][changed]==255))
   self.assertTrue(np.all(original['WeaponHandOccluder'][:,:,3][changed]==0))
   for role in ORDER:
    if role!='BodyCostume':self.assertTrue(np.array_equal(original[role],new[role]),role)
   self.assertEqual(compose(original).tobytes(),compose(new).tobytes())
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'fresh'):build(Path(tmp))

if __name__=='__main__':unittest.main()
