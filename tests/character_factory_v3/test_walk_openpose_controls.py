import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import build_walk_openpose_controls as study
class WalkControlsTests(unittest.TestCase):
 def test_replay_and_projection(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'controls';study.build(out);r=json.loads((out/'receipt.json').read_text());self.assertEqual(len(r['frames']),16)
   for i,row in enumerate(r['frames']):
    p=out/f'{i:03}.png';self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['image_sha256'])
    with Image.open(p) as im:self.assertEqual(im.size,(512,512))
    self.assertLess(max(row['projection_errors_source_px'].values()),.002)
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
