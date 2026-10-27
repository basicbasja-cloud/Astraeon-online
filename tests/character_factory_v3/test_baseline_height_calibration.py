import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from calibrate_baseline_height import baseline_height_fit
class BaselineHeightTests(unittest.TestCase):
 def test_standing_target_not_forced_to_crouched_height(self):
  r=baseline_height_fit(100,300,130,280,110,280,40,440)
  self.assertEqual(r['expected_body_height_px'],220);self.assertEqual(r['shared_scale'],.55)
 def test_same_pose_retains_baseline_height(self):
  r=baseline_height_fit(100,300,130,280,130,280,40,440)
  self.assertEqual(r['shared_scale'],.5)
 def test_invalid_observations_fail(self):
  with self.assertRaises(ValueError):baseline_height_fit(100,300,130,280,130,280,440,40)
