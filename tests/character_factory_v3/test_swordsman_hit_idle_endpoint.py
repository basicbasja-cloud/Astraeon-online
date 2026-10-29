import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_hit_idle_endpoint as audit
class IdleEndpointTests(unittest.TestCase):
 def test_quaternion_sign_equivalence(self):
  self.assertAlmostEqual(audit.angle([1,0,0,0],[-1,0,0,0]),0.)
  with self.assertRaises(ValueError):audit.angle([0,0,0,0],[1,0,0,0])
 def test_retained_study_matches_recorded_idle_landmarks(self):
  result=audit.audit();self.assertEqual(len(result['directions']),8)
  self.assertLess(max(x['world_landmark_max_m'] for x in result['directions'].values()),1e-5)
  self.assertLess(max(x['projected_landmark_max_authoring_px'] for x in result['directions'].values()),.001)
if __name__=='__main__':unittest.main()
