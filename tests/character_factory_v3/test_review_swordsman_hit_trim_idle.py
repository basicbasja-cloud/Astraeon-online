import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import review_swordsman_hit_trim_idle as review
class HitTrimReviewTests(unittest.TestCase):
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):review.make(Path(d),Path(d))
 def test_rejects_unrelated_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'source';source.mkdir();(source/'manifest.json').write_text(json.dumps({'job':{},'experimental_status':'NO'}))
   with self.assertRaises(ValueError):review.make(source,Path(d)/'out')
if __name__=='__main__':unittest.main()
