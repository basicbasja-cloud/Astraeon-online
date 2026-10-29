import sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_pickup_sw08_visible_cutout as proposal
class PickupVisibleCutoutTests(unittest.TestCase):
 def test_same_frame_layers_recompose_keyed_master(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';receipt=proposal.build(out);combined=Image.new('RGBA',(768,768))
   for role in proposal.ORDER:combined.alpha_composite(Image.open(out/'layers'/f'{role}.png').convert('RGBA'))
   self.assertEqual(combined.tobytes(),Image.open(out/'master.png').convert('RGBA').tobytes());self.assertTrue(receipt['exact_same_frame_recomposition']);self.assertTrue(all(v>0 for v in receipt['visible_pixels_by_role'].values()))
 def test_existing_output_is_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';out.mkdir();(out/'sentinel').write_bytes(b'keep')
   with self.assertRaisesRegex(ValueError,'fresh output'):proposal.build(out)
   self.assertEqual((out/'sentinel').read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
