import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_pickup_sw_sparse_foot_registration as study
class FootRegistrationTests(unittest.TestCase):
 def test_empty_proxy_rejected(self):
  with self.assertRaisesRegex(ValueError,'No brown foot'):study.boot_probe(Image.new('RGB',(384,384),'white'))
 def test_sparse_output_preserves_scale_and_is_unapproved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';r=study.build(out);self.assertEqual(len(r['frames']),5);self.assertFalse(r['runtime_admitted']);self.assertEqual(r['horizontal_translation'],0);self.assertEqual(len({x['sole_proxy_after_y']for x in r['frames']}),1)
   for row in r['frames']:
    with Image.open(out/'frames'/f"{row['frame']:03}.png") as im:self.assertEqual(im.size,(384,384))
    self.assertLessEqual(abs(row['additional_y']),25)
 def test_existing_output_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';out.mkdir();(out/'keep').write_bytes(b'keep')
   with self.assertRaisesRegex(ValueError,'fresh output'):study.build(out)
   self.assertEqual((out/'keep').read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
