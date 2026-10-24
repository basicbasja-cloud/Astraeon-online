import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_template_slot_variants import template_costume


class TemplateSlotVariantTests(unittest.TestCase):
    def test_new_paint_stays_inside_original_body_slot(self):
        original=np.zeros((24,24,4),np.uint8);original[5:19,5:19]=[100,80,60,255];original[5,5,3]=80
        template=Image.fromarray(original);paint=Image.new('RGBA',(24,24),(160,20,30,255));result,report=template_costume(template,paint);actual=np.array(result)
        np.testing.assert_array_equal(actual[:,:,3],original[:,:,3]);self.assertEqual(actual[10,10].tolist(),[160,20,30,255]);self.assertEqual(report['uncovered_interior_pixels'],0)
        np.testing.assert_array_equal(np.array(template),original)

    def test_missing_interior_is_reported_without_silent_paint_fill(self):
        template=Image.new('RGBA',(24,24),(80,70,60,255));paint=template.copy();paint.putpixel((12,12),(0,0,0,0))
        result,report=template_costume(template,paint);self.assertEqual(report['uncovered_interior_pixels'],1);self.assertEqual(result.getpixel((12,12)),(0,0,0,0))

    def test_different_canvases_are_rejected(self):
        with self.assertRaises(ValueError):template_costume(Image.new('RGBA',(24,24)),Image.new('RGBA',(20,20)))


if __name__=='__main__':unittest.main()
