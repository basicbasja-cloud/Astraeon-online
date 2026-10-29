import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_source_object_curves as audit
class SwordsmanSourceCurvesTest(unittest.TestCase):
 def test_action_names_deduplicated_sorted(self):
  factory={'classes':{'Swordsman':{'actions':{'a':{'source_actions':['B','A']},'b':{'source_actions':['A']},'c':{}}}}}
  self.assertEqual(audit.action_names(factory),['A','B'])
 def test_only_object_paths_are_considered(self):
  self.assertIn('location',audit.OBJECT_PATHS)
  self.assertNotIn('pose.bones["hand_r"].location',audit.OBJECT_PATHS)
if __name__=='__main__':unittest.main()
