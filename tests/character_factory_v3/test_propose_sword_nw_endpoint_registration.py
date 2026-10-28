import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from propose_sword_nw_endpoint_registration import move, alpha_centroid, lower_component

class WholeFrameRegistrationTests(unittest.TestCase):
    def test_translation_preserves_every_nontransparent_pixel_and_canvas(self):
        im=Image.new('RGBA',(32,32));im.putpixel((12,13),(20,40,60,255));im.putpixel((19,18),(10,20,30,128))
        translated=move(im,-8)
        self.assertEqual(translated.size,im.size)
        self.assertEqual(translated.getpixel((4,13)),(20,40,60,255))
        self.assertEqual(translated.getpixel((11,18)),(10,20,30,128))
        self.assertEqual(translated.getchannel('A').getbbox(),(4,13,12,19))
        self.assertEqual(im.getpixel((12,13)),(20,40,60,255))

    def test_translation_rejects_visible_clipping(self):
        im=Image.new('RGBA',(32,32));im.putpixel((1,10),(1,2,3,255))
        with self.assertRaisesRegex(ValueError,'clips'):move(im,-8)

    def test_empty_alpha_cannot_fake_landmarks(self):
        im=Image.new('RGBA',(768,768))
        with self.assertRaisesRegex(ValueError,'Empty'):alpha_centroid(im)
        with self.assertRaisesRegex(ValueError,'No identifiable'):lower_component(im)

if __name__=='__main__':unittest.main()
