import importlib.util
from pathlib import Path
import unittest

from PIL import Image, ImageDraw

PATH = Path(__file__).resolve().parents[2]/'tools/character_factory_v3/audit_painted_sheet.py'
spec = importlib.util.spec_from_file_location('painted_sheet_audit', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PaintedSheetAuditTests(unittest.TestCase):
    def fixture(self):
        image = Image.new('RGBA',(100,100))
        draw = ImageDraw.Draw(image)
        for x,y in [(0,0),(50,0),(0,50),(50,50)]:
            draw.rectangle((x+10,y+10,x+39,y+39),fill=(60,70,80,255))
        return image

    def test_padded_cells_pass_extraction_only(self):
        result = module.audit(self.fixture(),[2,2])
        self.assertTrue(result['extraction_gate_passed'])
        self.assertFalse(result['runtime_admitted'])
        self.assertFalse(result['paint_alignment_approved'])

    def test_cross_cell_art_is_rejected(self):
        image = self.fixture()
        ImageDraw.Draw(image).rectangle((48,10,52,20),fill='white')
        result = module.audit(image,[2,2])
        self.assertFalse(result['extraction_gate_passed'])
        self.assertFalse(result['frames'][0]['extraction_gate_passed'])
        self.assertFalse(result['frames'][1]['extraction_gate_passed'])

    def test_hidden_rgb_and_faint_alpha_do_not_define_bounds(self):
        image = self.fixture()
        image.putpixel((0,0),(255,0,0,0))
        image.putpixel((1,0),(255,0,0,1))
        self.assertTrue(module.audit(image,[2,2])['extraction_gate_passed'])

    def test_empty_cell_is_rejected(self):
        image = self.fixture()
        image.paste((0,0,0,0),(0,0,50,50))
        self.assertIn('empty_cell',module.audit(image,[2,2])['frames'][0]['blockers'])

    def test_fractional_grid_has_no_gaps_or_overlaps(self):
        result = module.audit(Image.new('RGBA',(101,99)),[3,2])
        boxes = [r['source_box'] for r in result['frames']]
        area = sum((b[2]-b[0])*(b[3]-b[1]) for b in boxes)
        self.assertEqual(area,101*99)
        self.assertEqual(boxes[-1][2:],[101,99])

    def test_saturated_red_is_diagnostic_not_generic_costume_rejection(self):
        image = self.fixture()
        image.putpixel((12,12),(255,0,0,255))
        result = module.audit(image,[2,2])
        self.assertTrue(result['extraction_gate_passed'])
        self.assertEqual(result['frames'][0]['saturated_red_pixels'],1)

    def test_invalid_grid_is_rejected(self):
        with self.assertRaises(ValueError):
            module.audit(self.fixture(),[True,2])


if __name__ == '__main__':
    unittest.main()
