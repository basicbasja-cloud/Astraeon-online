import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools/character_factory_v3"))
from build_occluded_underlays import add_hidden,composite,shaft_donor,solidify_interior,transfer_visible_pixels

class OccludedUnderlayTests(unittest.TestCase):
    def test_only_fully_opaque_foreground_hides_additions(self):
        body=Image.new("RGBA",(3,1));paint=Image.new("RGBA",(3,1),(120,80,40,255))
        cover=Image.new("RGBA",(3,1));cover.putdata([(1,2,3,255),(1,2,3,254),(0,0,0,0)])
        result,count=add_hidden(body,paint,cover,np.ones((1,3),bool))
        self.assertEqual(count,1)
        self.assertEqual(composite([body,cover]).tobytes(),composite([result,cover]).tobytes())
    def test_existing_paint_and_outside_recipe_are_preserved(self):
        body=Image.new("RGBA",(3,1));body.putpixel((0,0),(200,100,20,128))
        result,count=add_hidden(body,Image.new("RGBA",(3,1),"red"),Image.new("RGBA",(3,1),"blue"),np.array([[True,True,False]]))
        self.assertEqual(count,1);self.assertEqual(result.getpixel((0,0)),body.getpixel((0,0)))
        self.assertEqual(result.getpixel((2,0)),(0,0,0,0))
    def test_empty_shaft_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"No opaque"):
            shaft_donor(Image.new("RGBA",(32,32)),16,2,4,24)
    def test_hidden_shaft_stays_inside_authored_corridor(self):
        im=Image.new("RGBA",(32,32));im.putpixel((16,8),(140,80,20,255))
        donor,region=shaft_donor(im,16,2,4,24)
        self.assertEqual(donor.getpixel((16,16)),(140,80,20,255))
        self.assertEqual(donor.getpixel((4,16)),(0,0,0,0));self.assertFalse(region[2,16])
    def test_opacity_repair_preserves_rgb_and_soft_edges(self):
        im=Image.new("RGBA",(3,1));im.putdata([(120,80,20,250),(120,80,20,249),(0,0,0,0)])
        out,count=solidify_interior(im)
        self.assertEqual(count,1);self.assertEqual(out.getpixel((0,0)),(120,80,20,255))
        self.assertEqual(out.getpixel((1,0)),im.getpixel((1,0)))

    def test_visible_ownership_transfer_preserves_master(self):
        parts={"body":Image.new("RGBA",(2,1)),"head":Image.new("RGBA",(2,1))}
        parts["body"].putpixel((0,0),(180,80,30,190));before=composite(list(parts.values()))
        self.assertEqual(transfer_visible_pixels(parts,"body","head",np.array([[True,False]])),1)
        self.assertEqual(composite(list(parts.values())).tobytes(),before.tobytes())
    def test_visible_transfer_rejects_overwriting_existing_ownership(self):
        parts={"body":Image.new("RGBA",(2,1),"red"),"head":Image.new("RGBA",(2,1),"blue")}
        with self.assertRaisesRegex(ValueError,"overwrite"):
            transfer_visible_pixels(parts,"body","head",np.array([[True,False]]))
