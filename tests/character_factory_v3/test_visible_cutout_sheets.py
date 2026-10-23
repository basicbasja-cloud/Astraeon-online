import sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_visible_cutout_sheets import transfer_ownership,retain_weapon_underlay

class VisibleCutoutSheetTests(unittest.TestCase):
    def test_hidden_body_is_retained_only_beneath_opaque_weapon(self):
        weapon=Image.new('RGBA',(2,1));weapon.putdata([(30,40,50,255),(70,80,90,240)])
        original={'BodyCostume':Image.new('RGBA',(2,1)),'Weapon':weapon};donor=Image.new('RGBA',(2,1),(110,80,40,255))
        parts,count=retain_weapon_underlay(original,donor)
        self.assertEqual(count,1);self.assertEqual(parts['BodyCostume'].getpixel((0,0)),donor.getpixel((0,0)));self.assertEqual(parts['BodyCostume'].getpixel((1,0))[3],0)
        self.assertEqual(Image.alpha_composite(parts['BodyCostume'],weapon).tobytes(),weapon.tobytes());self.assertIsNone(original['BodyCostume'].getbbox())
    def test_masks_transfer_ownership_without_resampling_canonical_pixels(self):
        a=np.zeros((32,32,4),dtype=np.uint8);a[8:24,8:24]=[150,70,30,155];master=Image.fromarray(a);head=Image.new('L',(64,64));ImageDraw.Draw(head).rectangle((0,0,63,27),fill=255);weapon=Image.new('L',(64,64));ImageDraw.Draw(weapon).rectangle((44,36,63,63),fill=255)
        parts=transfer_ownership(master,{'HeadHair':head,'Weapon':weapon},[8,8,16,16]);combined=Image.new('RGBA',master.size)
        for im in parts.values():combined.alpha_composite(im)
        np.testing.assert_array_equal(np.asarray(combined),a)
        self.assertTrue(all(np.count_nonzero(np.asarray(im)[:,:,3])for im in parts.values()))
    def test_overlapping_masks_rejected(self):
        mask=Image.new('L',(8,8),255)
        with self.assertRaisesRegex(ValueError,'Overlapping'):transfer_ownership(Image.new('RGBA',(16,16)),{'HeadHair':mask,'Weapon':mask},[0,0,8,8])
    def test_invalid_shared_viewport_rejected(self):
        for viewport in [[-1,0,8,8],[0,0,17,8],[0,0,8,0],[0,0,8,True]]:
            with self.assertRaisesRegex(ValueError,'viewport'):transfer_ownership(Image.new('RGBA',(16,16)),{'HeadHair':Image.new('L',(8,8))},viewport)
if __name__=='__main__':unittest.main()
