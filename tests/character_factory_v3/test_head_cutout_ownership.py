import sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from refine_head_cutout_ownership import refine

class HeadOwnershipTests(unittest.TestCase):
    def test_warm_fringe_moves_to_head_without_changing_master_or_green_collar(self):
        head=Image.new('RGBA',(20,20));body=Image.new('RGBA',(20,20));ImageDraw.Draw(head).rectangle((5,3,12,13),fill=(100,60,30,255));body.putpixel((4,6),(100,60,30,160));body.putpixel((13,6),(40,80,50,255));body.putpixel((4,13),(110,70,30,255));before=Image.alpha_composite(body,head)
        h,b,report=refine(head,body,radius=1,neckline_band=2);self.assertEqual(Image.alpha_composite(b,h).tobytes(),before.tobytes());self.assertEqual(h.getpixel((4,6)),(100,60,30,160));self.assertEqual(b.getpixel((13,6)),(40,80,50,255));self.assertEqual(b.getpixel((4,13)),(110,70,30,255));self.assertFalse(report['pixel_translation'])
    def test_neutral_weapon_line_and_isolated_neck_skin_leave_the_head_layer(self):
        head=Image.new('RGBA',(20,20));body=Image.new('RGBA',(20,20));ImageDraw.Draw(head).rectangle((4,3,10,10),fill=(90,50,25,255));ImageDraw.Draw(head).rectangle((9,5,12,7),fill=(235,230,220,255));head.putpixel((7,14),(220,175,130,255));before=Image.alpha_composite(body,head)
        h,b,report=refine(head,body,radius=1,neckline_band=2);self.assertEqual(h.getpixel((12,6))[3],0);self.assertEqual(b.getpixel((12,6)),(235,230,220,255));self.assertEqual(h.getpixel((7,14))[3],0);self.assertEqual(b.getpixel((7,14)),(220,175,130,255));self.assertEqual(Image.alpha_composite(b,h).tobytes(),before.tobytes())
    def test_manual_profile_excludes_adjacent_glove_without_moving_any_pixels(self):
        head=Image.new('RGBA',(20,20));body=Image.new('RGBA',(20,20));ImageDraw.Draw(head).rectangle((4,3,15,12),fill=(90,50,25,255));before=Image.alpha_composite(body,head);h,b,report=refine(head,body,radius=1,neckline_band=2,right_profile=[[10,0],[10,20]])
        self.assertEqual(h.getpixel((14,6))[3],0);self.assertEqual(b.getpixel((14,6)),(90,50,25,255));self.assertEqual(Image.alpha_composite(b,h).tobytes(),before.tobytes());self.assertGreater(report['manual_hand_weapon_exclusion_pixels'],0)

if __name__=='__main__':unittest.main()
