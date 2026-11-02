import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import propose_nw003_body_edge_cleanup as study
class BodyEdgeTests(unittest.TestCase):
 def test_cleanup_is_bounded_and_corrected_layers_recompose(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'result';receipt=study.build(out);self.assertGreater(receipt['selected_body_pixels'],0)
   before=np.asarray(Image.open(study.SLOTS/'BodyCostume.png').convert('RGBA'));after=np.asarray(Image.open(out/'BodyCostume.png').convert('RGBA'));mask=np.asarray(Image.open(out/'edge-mask.png'))>0
   np.testing.assert_array_equal(before[~mask],after[~mask]);combined=Image.fromarray(after.copy())
   for role in ('HeadHair.png','Weapon.png'):
    with Image.open(study.SLOTS/role) as im:combined.alpha_composite(im.convert('RGBA'))
   np.testing.assert_array_equal(np.asarray(combined),np.asarray(Image.open(out/'corrected-master.png').convert('RGBA')))
   with self.assertRaises(ValueError):study.build(out)
if __name__=='__main__':unittest.main()
