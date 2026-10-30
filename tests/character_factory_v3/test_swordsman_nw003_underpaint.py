import sys, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'))
import propose_swordsman_nw003_underpaint as study

class UnderpaintTests(unittest.TestCase):
    def test_outside_mask_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result'; r=study.build(out)
            self.assertTrue(r['outside_mask_exact'])
            original=Image.new('RGBA',(512,512))
            for role in ('BodyCostume','HeadHair','WeaponHandOccluder'):
                with Image.open(study.base.SOURCE/role/'003.png') as im:original.alpha_composite(im.convert('RGBA'))
            candidate=np.asarray(Image.open(out/'complete-master-no-weapon.png').convert('RGBA'))
            mask=np.asarray(Image.open(out/'mask.png'))>0
            np.testing.assert_array_equal(candidate[~mask],np.asarray(original)[~mask])
            with self.assertRaises(ValueError):study.build(out)

if __name__ == '__main__': unittest.main()
