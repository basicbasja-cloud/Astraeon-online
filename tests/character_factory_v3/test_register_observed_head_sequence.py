import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from register_observed_head_sequence import translate_frame


class PackingRegistrationTests(unittest.TestCase):
    def test_integer_translation_preserves_all_source_rgba(self):
        image=Image.new('RGBA',(20,20));image.putpixel((5,6),(90,60,30,128));image.putpixel((6,6),(90,60,30,255))
        result=translate_frame(image,[2,-3])
        self.assertEqual(result.getpixel((7,3)),(90,60,30,128));self.assertEqual(result.getpixel((8,3)),(90,60,30,255))
        self.assertEqual(np.array(image.getchannel('A')).sum(),np.array(result.getchannel('A')).sum())
    def test_clipping_and_fractional_registration_are_rejected(self):
        image=Image.new('RGBA',(20,20));image.putpixel((0,0),(90,60,30,255))
        with self.assertRaisesRegex(ValueError,'clips'):translate_frame(image,[-1,0])
        with self.assertRaisesRegex(ValueError,'integer'):translate_frame(image,[.5,0])
