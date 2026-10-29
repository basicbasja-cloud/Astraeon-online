import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import review_swordsman_hit_sw_sheet as review
class HitSheetTest(unittest.TestCase):
 def test_square_source_crop_only(self):
  self.assertEqual(review.square_crop((448,520,1088,1160)),(448,520,1088,1160))
  with self.assertRaises(ValueError):review.square_crop((448,520,1088,1200))
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):review.review(Path(d))
 def test_real_review_records_source_pose_equality(self):
  with tempfile.TemporaryDirectory() as d:
   r=review.review(Path(d)/'out')
   self.assertEqual(r['frames'],12)
   self.assertEqual(r['same_source_pose_00_vs_11_foreground_difference'][0]['different_pixels_in_union'],0)
   self.assertGreater(r['same_source_pose_00_vs_11_foreground_difference'][1]['different_pixels_in_union'],0)
if __name__=='__main__':unittest.main()
