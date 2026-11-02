import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_nw003_three_slots as slots
import propose_nw003_alt_head_swap as swap
class OwnershipTests(unittest.TestCase):
 def test_reconstructs_same_master_and_head_swap_preserves_outside(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);a=root/'slots';b=root/'swap';self.assertEqual(slots.build(a)['visible_rgba_difference_pixels'],0);self.assertEqual(swap.build(b)['outside_union_difference'],0)
   master=np.asarray(Image.open(slots.SOURCE).convert('RGBA'));recomposed=np.asarray(Image.open(a/'recomposed.png').convert('RGBA'));np.testing.assert_array_equal(master,recomposed)
   with self.assertRaises(ValueError):slots.build(a)
if __name__=='__main__':unittest.main()
