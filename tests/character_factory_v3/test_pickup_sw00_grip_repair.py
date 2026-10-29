import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_pickup_sw00_grip_repair as repair
class GripRepairTests(unittest.TestCase):
 def test_bounded_repair_preserves_pixels_outside_mask(self):
  donor=repair.BASE/'donor-short-blade.png'
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';receipt=repair.build(out,donor);a=np.array(Image.open(repair.BASE/'initial.png').convert('RGB'));b=np.array(Image.open(out/'candidate.png').convert('RGB'));mask=np.array(Image.open(out/'repair-mask.png'));self.assertTrue(np.array_equal(a[mask==0],b[mask==0]));self.assertGreater(receipt['changed_pixels'],0);self.assertEqual(receipt['outside_mask_changed_pixels'],0)
 def test_existing_output_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';out.mkdir();(out/'keep').write_bytes(b'saved')
   with self.assertRaisesRegex(ValueError,'fresh output'):repair.build(out)
   self.assertEqual((out/'keep').read_bytes(),b'saved')
if __name__=='__main__':unittest.main()
