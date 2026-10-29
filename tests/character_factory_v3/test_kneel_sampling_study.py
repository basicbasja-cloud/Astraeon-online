import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from render_kneel_pickup_sampling_study import validate_samples
class SamplingStudyTests(unittest.TestCase):
 def test_valid_explicit_samples(self):
  a=[0,5,30,125,156];self.assertEqual(validate_samples({'source_actions':['Fixing_Kneeling'],'loop':False,'frames':5,'study_source_frames':a}),a)
 def test_invalid_samples_rejected(self):
  for a in ([0,5,5],[0,10,4],[0,float('nan'),10],[0,True,10],[-1,0,5]):
   with self.subTest(a=a):
    with self.assertRaises(ValueError):validate_samples({'source_actions':['Fixing_Kneeling'],'loop':False,'frames':3,'study_source_frames':a})
 def test_multi_action_and_loop_rejected(self):
  for j in ({'source_actions':['A','B'],'loop':False},{'source_actions':['A'],'loop':True}):
   with self.assertRaises(ValueError):validate_samples({**j,'frames':2,'study_source_frames':[0,1]})
if __name__=='__main__':unittest.main()
