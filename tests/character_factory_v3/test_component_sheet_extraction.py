import importlib.util
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

PATH = Path(__file__).resolve().parents[2]/'tools/character_factory_v3/extract_component_sheet.py'
spec = importlib.util.spec_from_file_location('component_sheet', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ComponentSheetTests(unittest.TestCase):
    def fixture(self):
        image = Image.new('RGBA',(100,100))
        draw = ImageDraw.Draw(image)
        for box in [(40,10,54,30),(65,10,85,30),(10,65,30,85),(65,65,85,85)]:
            draw.rectangle(box,fill=(110,60,40,255))
        return image

    def test_complete_cross_cell_component_is_retained(self):
        pixels,owners,found = module.components(self.fixture(),[2,2],[50,50],20)
        self.assertEqual(len(found),4)
        self.assertGreater(found[0]['box'][2],50)
        selected = owners==found[0]['label']
        self.assertEqual(np.count_nonzero(pixels[:,:,3][selected]),15*21)

    def test_joined_figures_are_rejected(self):
        image = self.fixture()
        ImageDraw.Draw(image).line((50,20,75,20),fill='white',width=2)
        with self.assertRaisesRegex(ValueError,'one complete independent'):
            module.components(image,[2,2],[50,50],20)

    def test_missing_pose_is_rejected(self):
        image = self.fixture()
        image.paste((0,0,0,0),(60,60,90,90))
        with self.assertRaisesRegex(ValueError,'one complete independent'):
            module.components(image,[2,2],[50,50],20)

    def test_globally_clipped_art_is_rejected(self):
        image = self.fixture()
        ImageDraw.Draw(image).rectangle((0,65,30,85),fill='white')
        with self.assertRaisesRegex(ValueError,'outer sheet edge'):
            module.components(image,[2,2],[50,50],20)


if __name__ == '__main__':
    unittest.main()
