import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools/character_factory_v3"))
from normalize_single_art_template import calibrate

class SingleTemplateTests(unittest.TestCase):
    def test_identity_preserves_visible_rgba(self):
        im=Image.new("RGBA",(16,16)); im.putpixel((8,8),(120,80,40,173))
        self.assertEqual(calibrate(im,1,[0,0]).tobytes(),im.tobytes())
    def test_translation_moves_one_template_without_rescaling(self):
        im=Image.new("RGBA",(16,16)); im.putpixel((8,8),(120,80,40,255))
        self.assertEqual(calibrate(im,1,[2,-1]).getpixel((10,7)),(120,80,40,255))
    def test_invalid_static_calibrations_are_rejected(self):
        im=Image.new("RGBA",(16,16))
        for scale,offset in [(0,[0,0]),(float("nan"),[0,0]),(1,[float("inf"),0]),(1,[257,0])]:
            with self.subTest(scale=scale,offset=offset):
                with self.assertRaises(ValueError): calibrate(im,scale,offset)
