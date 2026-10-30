import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import review_swordsman_skill_dense as r
class DenseSkillTests(unittest.TestCase):
 def test_metrics_scale_to_runtime_and_cover_directions(self):
  def frame(x):return {'landmarks':{'head':[x,0],'hand_r':[x,0]},'weapon_guide':{'tip':[x,0]}}
  m={'job':{'resolution':768},'views':{d:{'frames':[frame(0),frame(32)]} for d in r.DIRS}}
  result=r.metrics(m);self.assertEqual(len(result),4);self.assertEqual(result['SW'][0]['tip_runtime_px'],10.)
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):r.build(Path(d),Path(d))
if __name__=='__main__':unittest.main()
