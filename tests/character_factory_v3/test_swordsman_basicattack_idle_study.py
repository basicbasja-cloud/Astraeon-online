import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import render_swordsman_basicattack_idle_study as render
import review_swordsman_basicattack_idle_study as review
class BasicAttackIdleStudyTests(unittest.TestCase):
 def setUp(self):
  p=Path(__file__).resolve().parents[2]/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-basicattack-idle-study-20261030/job.json';self.job=json.loads(p.read_text())
 def test_retained_frames_and_explicit_transition(self):
  s=render.samples(self.job);self.assertEqual([x['source_frame'] for x in s[:16]],self.job['explicit_source_samples']);self.assertEqual([x['transition_weight'] for x in s[16:]],[.25,.5,.75,1.]);self.assertEqual(s[-1]['action'],'Idle_Sword')
 def test_reject_changed_order_and_loop(self):
  self.job['explicit_source_samples'][2]=self.job['explicit_source_samples'][1]
  with self.assertRaises(ValueError):render.samples(self.job)
  self.job['loop']=True
  with self.assertRaises(ValueError):render.samples(self.job)
 def test_quaternion_equivalence(self):self.assertAlmostEqual(review.quat_angle([1,0,0,0],[-1,0,0,0]),0.)
if __name__=='__main__':unittest.main()
