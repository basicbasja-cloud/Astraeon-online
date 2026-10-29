import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from kneel_pickup_reach_study import reach_weight,leg_weight
class ReachStudyTests(unittest.TestCase):
 def test_reach_ramps_without_changing_endpoints(self):
  self.assertEqual([reach_weight(x) for x in [0,10,25,35,125,135,150,156]],[0.,0.,1.,1.,1.,1.,0.,0.])
  self.assertAlmostEqual(reach_weight(17.5),.5);self.assertAlmostEqual(reach_weight(142.5),.5)
 def test_nonfinite_phase_rejected(self):
  for value in [float('nan'),float('inf'),-float('inf')]:
   with self.assertRaises(ValueError):reach_weight(value)
   with self.assertRaises(ValueError):leg_weight(value)
 def test_leg_weight_preserves_endpoints(self):
  self.assertEqual([leg_weight(x) for x in [0,15,35,125,141,156]],[0.,1.,1.,1.,1.,0.])
  self.assertAlmostEqual(leg_weight(7.5),.5)
if __name__=='__main__':unittest.main()
