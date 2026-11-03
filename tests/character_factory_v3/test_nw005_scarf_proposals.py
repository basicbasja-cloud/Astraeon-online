import sys, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_nw005_scarf_ownership as ownership
import propose_nw005_scarf_underpaint as underpaint

def rgba(path): return np.asarray(Image.open(path).convert('RGBA'))

class ScarfProposalTests(unittest.TestCase):
 def test_transfer_and_hidden_surface_are_bounded_and_recompose(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); transferred=root/'transfer'; filled=root/'fill'
   a=ownership.build(transferred); b=underpaint.build(filled,transferred)
   self.assertGreater(a['transferred_pixels'],0); self.assertGreater(b['underpaint_pixels'],0)
   mask=np.asarray(Image.open(transferred/'scarf-transfer-mask.png'))>0
   oldbody=rgba(ownership.O/'BodyCostume.png'); oldweapon=rgba(ownership.O/'Weapon.png')
   body=rgba(transferred/'BodyCostume.png'); weapon=rgba(transferred/'Weapon.png')
   np.testing.assert_array_equal(body[mask],oldweapon[mask]);np.testing.assert_array_equal(body[~mask],oldbody[~mask]);np.testing.assert_array_equal(weapon[~mask],oldweapon[~mask]);self.assertTrue(np.all(weapon[mask]==0))
   mask2=np.asarray(Image.open(filled/'underpaint-mask.png'))>0; newbody=rgba(filled/'BodyCostume.png')
   self.assertTrue(np.all(weapon[:,:,3][mask2]==255));self.assertTrue(np.all(body[:,:,3][mask2]==0));np.testing.assert_array_equal(newbody[~mask2],body[~mask2])
   master=rgba(ownership.SRC/'Master/005.png');np.testing.assert_array_equal(master,rgba(transferred/'recomposed.png'));np.testing.assert_array_equal(master,rgba(filled/'recomposed.png'))
   with self.assertRaises(ValueError):ownership.build(transferred)
   with self.assertRaises(ValueError):underpaint.build(filled,transferred)
if __name__=='__main__': unittest.main()
