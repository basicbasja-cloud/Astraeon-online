import sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import propose_sword_nw15_detached_blade_cleanup as proposal

class DetachedBladeCleanupTests(unittest.TestCase):
 def test_reassigns_only_five_pixels_and_preserves_composite(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';receipt=proposal.build(out)
   self.assertEqual(receipt['transferred_count'],5)
   original=np.array(Image.open(proposal.SOURCE/'BodyCostume.png'));new=np.array(Image.open(out/'layers/BodyCostume.png'))
   changed=np.any(original!=new,axis=2);self.assertEqual(int(changed.sum()),5)
   self.assertEqual(Image.open(out/'master.png').tobytes(),Image.open(proposal.SOURCE.parent/'master.png').tobytes())
   old_preview=np.array(Image.open(proposal.SOURCE.parent/'no-weapon-preview.png'));new_preview=np.array(Image.open(out/'no-weapon-preview.png'))
   self.assertEqual(int(np.any(old_preview!=new_preview,axis=2).sum()),5)
 def test_existing_destination_is_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'draft';out.mkdir();sentinel=out/'sentinel';sentinel.write_text('retain')
   with self.assertRaisesRegex(ValueError,'fresh output'):proposal.build(out)
   self.assertEqual(sentinel.read_text(),'retain')

if __name__=='__main__':unittest.main()
