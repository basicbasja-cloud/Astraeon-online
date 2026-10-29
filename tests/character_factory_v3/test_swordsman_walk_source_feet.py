import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_walk_source_feet as audit
class WalkSourceFeetTests(unittest.TestCase):
 def test_referenced_guide_is_native_walk_loop(self):
  g=json.loads(audit.GUIDE.read_text());self.assertEqual(g['job']['source_actions'],['Walk']);self.assertTrue(g['job']['loop']);self.assertEqual(len(g['views']['SW']['frames']),16)
 def test_frame_roots_record_no_horizontal_motion(self):
  g=json.loads(audit.GUIDE.read_text());self.assertTrue(all(all(abs(v)<1e-6 for v in f['actor_root_delta']) for f in g['views']['SW']['frames']))
if __name__=='__main__':unittest.main()
