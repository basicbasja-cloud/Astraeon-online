import sys
from pathlib import Path
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from replace_native_shoe_patches import shoe_patch,complete_background_shoe


class NativeShoePatchTests(unittest.TestCase):
    def test_unrelated_mask_fragments_do_not_remove_the_other_leg(self):
        body=Image.new('RGBA',(64,64));body.paste((80,50,30,255),(30,30,50,60));body.paste((30,40,50,255),(5,5,10,10))
        mask=Image.new('RGBA',(64,64));mask.paste((80,50,30,255),(30,30,50,60));mask.paste((30,40,50,255),(5,5,10,10))
        new=Image.new('RGBA',(64,64));new.paste((100,70,40,255),(28,35,50,62))
        actual,report=shoe_patch(body,mask,new,[40,10],[40,40],True)
        self.assertEqual(actual.getpixel((6,6)),body.getpixel((6,6)));self.assertEqual(report['visible_changes_outside_patch'],0)
    def test_background_completion_preserves_every_opaque_body_pixel(self):
        body=Image.new('RGBA',(64,64));body.paste((80,50,30,255),(30,30,50,60));new=Image.new('RGBA',(64,64));new.paste((100,70,40,255),(25,35,50,62))
        actual,report=complete_background_shoe(body,new,[40,10],[40,40])
        self.assertEqual(actual.getpixel((35,40)),body.getpixel((35,40)));self.assertEqual(actual.getpixel((26,40)),(100,70,40,255));self.assertEqual(report['opaque_existing_body_pixels_changed'],0)
