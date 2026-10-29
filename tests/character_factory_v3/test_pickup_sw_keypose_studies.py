import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_pickup_sw16_head_repair as head
import review_pickup_sw_keyposes as review
class PickupKeyposeStudiesTests(unittest.TestCase):
 def test_bounded_head_edit_does_not_change_outside_mask(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'head';r=head.build(out);initial=np.array(Image.open(head.INITIAL).convert('RGB'));candidate=np.array(Image.open(out/'candidate.png').convert('RGB'));mask=np.array(Image.open(out/'repair-mask.png'));self.assertTrue(np.array_equal(initial[mask==0],candidate[mask==0]));self.assertEqual(r['outside_mask_changed_pixels'],0);self.assertGreater(r['changed_pixels'],0)
 def test_three_keyposes_do_not_claim_sequence(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'review';r=review.build(out);self.assertEqual([f['frame']for f in r['frames']],[0,8,16]);self.assertEqual(r['shared_offset_px'],(0,17));self.assertFalse(r['runtime_admitted'])
if __name__=='__main__':unittest.main()
