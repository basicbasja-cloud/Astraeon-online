import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_hit_blade_clearance as audit
class HitBladeClearanceTest(unittest.TestCase):
 def test_is_scoped_to_frozen_hit_job(self):
  job=json.loads(audit.JOB.read_text())
  self.assertEqual(job['source_actions'],['Hit_Chest'])
  self.assertTrue(job['freeze_source_object_transform'])
  self.assertEqual(job['frames'],12)
 def test_pose_curves_not_object_channels(self):
  self.assertNotIn('pose.bones["hand_r"].location',audit.CHANNELS)
if __name__=='__main__':unittest.main()
