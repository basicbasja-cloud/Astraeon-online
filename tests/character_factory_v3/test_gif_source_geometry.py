import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from audit_gif_source_geometry import compare

class GifGeometryTests(unittest.TestCase):
    def source(self):
        im=Image.new('RGB',(40,40),'#ddd')
        ImageDraw.Draw(im).polygon([(5,4),(15,8),(24,31),(7,27)],fill='#753814')
        return im
    def test_palette_change_does_not_imply_translation(self):
        source=self.source()
        result=compare(source,source.quantize(colors=4).convert('RGB'))
        self.assertEqual(result['best_decode_translation_xy'],[0,0])
    def test_actual_one_pixel_shift_is_detected(self):
        source=self.source()
        result=compare(source,ImageChops.offset(source,1,-1))
        self.assertEqual(result['best_decode_translation_xy'],[1,-1])
    def test_different_canvas_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'dimensions'):
            compare(self.source(),Image.new('RGB',(39,40)))

    def test_flat_tied_image_does_not_fabricate_a_shift(self):
        source=Image.new('RGB',(40,40),'#ddd')
        self.assertEqual(compare(source,source)['best_decode_translation_xy'],[0,0])
