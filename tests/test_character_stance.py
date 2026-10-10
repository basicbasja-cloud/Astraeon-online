import importlib.util
from pathlib import Path
import unittest
from PIL import Image,ImageDraw
spec=importlib.util.spec_from_file_location('stance',Path(__file__).resolve().parents[1]/'tools/audit_character_stance.py')
stance=importlib.util.module_from_spec(spec);spec.loader.exec_module(stance)

class StanceTests(unittest.TestCase):
    def test_detects_drift_without_moving_pixels(self):
        image=Image.new('RGBA',(80,40));draw=ImageDraw.Draw(image)
        draw.rectangle((10,20,19,30),fill='white');draw.rectangle((53,20,62,30),fill='white')
        before=image.tobytes();result=stance.measure(image,[40,40],{'right':[5,15,30,35]},1,2)
        self.assertEqual(result['findings'],[{'pose':1,'foot':'right','driftPixels':3.0}])
        self.assertEqual(image.tobytes(),before);self.assertFalse(result['visualApproval'])

    def test_empty_or_clipped_region_is_not_a_valid_measurement(self):
        image=Image.new('RGBA',(40,40))
        with self.assertRaisesRegex(ValueError,'Empty'):stance.measure(image,[40,40],{'right':[5,15,30,35]})
        ImageDraw.Draw(image).rectangle((5,20,19,30),fill='white')
        with self.assertRaisesRegex(ValueError,'boundary'):stance.measure(image,[40,40],{'right':[5,15,30,35]})

if __name__=='__main__':unittest.main()
