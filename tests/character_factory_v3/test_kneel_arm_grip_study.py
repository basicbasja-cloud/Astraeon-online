import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from render_kneel_arm_grip_study import validate
class ArmStudyTests(unittest.TestCase):
 def job(self):return {'source_actions':['Fixing_Kneeling'],'loop':False,'frames':3,'study_source_frames':[0,35,156],'study_arm_axis':'X','study_arm_degrees':-30}
 def test_valid_isolated_arm_study(self):validate(self.job())
 def test_invalid_adjustments_rejected(self):
  for key,value in [('study_arm_axis','Q'),('study_arm_degrees',51),('study_arm_degrees',float('nan')),('study_arm_degrees',True),('study_closed_fingers',1),('study_source_frames',[1,35,156])]:
   with self.subTest(key=key,value=value):
    job=self.job();job[key]=value
    with self.assertRaises(ValueError):validate(job)
if __name__=='__main__':unittest.main()
