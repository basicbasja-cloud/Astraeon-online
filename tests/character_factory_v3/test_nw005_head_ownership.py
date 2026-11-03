import hashlib,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_nw005_head_ownership as study
class OwnershipTests(unittest.TestCase):
 def test_reconstructs_original_and_preserves_sources(self):
  paths=[study.SRC/k/'005.png' for k in study.ORDER];before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'result';proof=study.build(out);self.assertEqual(proof['visible_rgba_mismatch'],0);self.assertGreater(proof['moves']['Weapon'],0)
   original=np.asarray(Image.open(study.SRC/'Master/005.png').convert('RGBA'));result=np.asarray(Image.open(out/'recomposed.png').convert('RGBA'));np.testing.assert_array_equal(original,result)
   with self.assertRaises(ValueError):study.build(out)
  self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
if __name__=='__main__':unittest.main()
