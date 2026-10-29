import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import review_swordsman_walk_fourframe_boots as review
class WalkFourFrameBootTests(unittest.TestCase):
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):review.build(Path(d))
 def test_four_sources_are_bound_and_unapproved(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'out';r=review.build(out)
   self.assertEqual(r['status'],'FOUR_FRAME_BOOT_REPAINT_STUDY_NOT_APPROVED')
   self.assertEqual([x['frame'] for x in r['frames']],[0,1,2,3]);self.assertEqual(len(list((out/'frames').glob('*.png'))),4)
if __name__=='__main__':unittest.main()
