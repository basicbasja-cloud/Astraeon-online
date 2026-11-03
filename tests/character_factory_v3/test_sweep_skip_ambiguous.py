import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_swordsman_sweep_skip_ambiguous as study
class SweepStudyTests(unittest.TestCase):
 def test_single_uncertain_key_is_excluded_and_others_match(self):
  samples=[{'grip':[float(i),0.0],'tip':[float(i)+100.,0.0]} for i in range(65)]
  annotations=[{'weapon_grip':[float(i*16),0.0],'weapon_tip':[float(i*16)+(20. if i==3 else 100.),0.0]} for i in range(5)]
  path,receipt=study.mapped_path(samples,annotations)
  self.assertEqual(receipt['excluded_key_indices'],[3]);self.assertEqual(len(path),65)
  for i in (0,1,2,4):
   for j,key in enumerate(('weapon_grip','weapon_tip')):np.testing.assert_allclose(path[16*i][j],annotations[i][key],atol=1e-6)
 def test_degenerate_annotation_is_rejected(self):
  samples=[{'grip':[0.,0.],'tip':[100.,0.]}]*65
  anns=[{'weapon_grip':[0.,0.],'weapon_tip':[0.,0.]}]*5
  with self.assertRaises(ValueError):study.mapped_path(samples,anns)
if __name__=='__main__':unittest.main()
