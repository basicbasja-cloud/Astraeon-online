import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'))
import build_swordsman_skill_sw_keypose_guide as guide
import review_swordsman_skill_sw_keyposes as review

class SkillPoseReviewTest(unittest.TestCase):
 def test_indices_match_and_do_not_claim_all_frames(self):
  self.assertEqual(guide.POSES, review.POSES)
  self.assertEqual(len(review.POSES), 8)
  self.assertEqual(review.POSES[-1], 31)
 def test_bounds_ignores_top_left_label(self):
  image=Image.new('RGB',(100,100),'white');image.putpixel((5,5),(0,0,0));image.putpixel((50,50),(0,0,0))
  self.assertEqual(review.bounds(image),[50,50,51,51])
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as directory:
   with self.assertRaises(ValueError): review.build(Path(directory))

if __name__=='__main__': unittest.main()
