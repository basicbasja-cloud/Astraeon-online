import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import review_swordsman_walk_fourframe_candidate as candidate
class WalkFourFrameCandidateTests(unittest.TestCase):
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):candidate.make(Path(d))
 def test_four_poses_and_unapproved_status(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'out';receipt=candidate.make(out)
   self.assertEqual(receipt['status'],'FOUR_FRAME_CANDIDATE_NOT_APPROVED')
   self.assertEqual([f['frame'] for f in receipt['frames']],[0,1,2,3])
   self.assertEqual(len(list((out/'frames').glob('*.png'))),4)
if __name__=='__main__':unittest.main()
