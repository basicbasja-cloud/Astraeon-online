import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/character_factory_v3'))
import propose_swordsman_nw008_blade_ownership as study

class BladeOwnershipTests(unittest.TestCase):
    def test_proposal_transfers_tip_without_changing_composite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'result'
            receipt = study.build(out)
            self.assertTrue(receipt['composite_exact_rgba'])
            self.assertEqual(receipt['transferred_nontransparent_pixels'], 68)
            self.assertEqual(receipt['scarf_pixels_returned_to_body'], 190)
            self.assertEqual(Image.open(out / 'BodyCostume.png').getpixel((280, 227))[3], 0)
            source = Image.open(study.SOURCE / 'BodyCostume' / '008.png').convert('RGBA')
            self.assertEqual(Image.open(out / 'Weapon.png').getpixel((280, 227)), source.getpixel((280, 227)))
            mask = (np.asarray(Image.open(out / 'transfer-mask.png')) > 0) | (np.asarray(Image.open(out / 'scarf-return-mask.png')) > 0)
            body = np.asarray(Image.open(out / 'BodyCostume.png'))
            np.testing.assert_array_equal(body[~mask], np.asarray(source)[~mask])
            with self.assertRaises(ValueError): study.build(out)

if __name__ == '__main__': unittest.main()
