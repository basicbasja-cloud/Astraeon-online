import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_independent_mage_kit import clean_single_part,split_arm,place,fill_hidden_clothing
from build_occluded_underlays import composite

class IndependentMageKitTests(unittest.TestCase):
    def test_underpaint_only_fills_missing_cloth_beneath_original_weapon(self):
        body=Image.new('RGBA',(8,8));body.putpixel((3,3),(20,30,40,128))
        donor=Image.new('RGBA',(8,8),(100,90,80,255));weapon=Image.new('RGBA',(8,8))
        for xy in [(2,2),(3,3),(7,7)]:weapon.putpixel(xy,(40,20,0,255))
        result,count=fill_hidden_clothing(body,donor,weapon,[1,1,5,5])
        self.assertEqual(count,1);self.assertEqual(result.getpixel((2,2)),(100,90,80,255))
        self.assertEqual(result.getpixel((3,3)),body.getpixel((3,3)))
        self.assertEqual(result.getpixel((7,7)),(0,0,0,0));self.assertEqual(result.getpixel((4,4)),(0,0,0,0))
    def test_underpaint_refuses_invalid_bounds(self):
        image=Image.new('RGBA',(8,8))
        with self.assertRaisesRegex(ValueError,'region'):fill_hidden_clothing(image,image,image,[-1,0,4,4])
    def test_small_detached_foreign_pixels_are_removed(self):
        im=Image.new('RGBA',(32,32));a=np.array(im);a[8:16,8:16]=(120,80,40,255);a[2,25]=(140,90,30,157);a[7,10]=(120,80,40,18)
        result,report=clean_single_part(Image.fromarray(a))
        self.assertEqual(report['removed_pixels'],1);self.assertEqual(report['maximum_removed_alpha'],157)
        self.assertEqual(result.getpixel((10,7)),(120,80,40,18))
        self.assertEqual(result.getpixel((25,2)),(0,0,0,0))
    def test_large_second_object_requires_review(self):
        im=Image.new('RGBA',(64,64));a=np.array(im);a[1:31,1:31]=(120,80,40,255);a[40:52,40:52]=(120,80,40,255)
        with self.assertRaisesRegex(ValueError,'semantic review'):clean_single_part(Image.fromarray(a))
    def test_complete_arm_split_preserves_semtransparent_edges(self):
        im=Image.new('RGBA',(32,32));a=np.array(im);a[9:13,2:24]=(120,80,40,255);a[9,5]=(120,80,40,128)
        points={'UpperArm.L':[23,11],'Forearm.L':[14,11],'Hand.L':[5,11]}
        source=Image.fromarray(a);parts=split_arm(source,'L',points,2)
        self.assertEqual(composite(list(parts.values())).tobytes(),source.tobytes())
    def test_invalid_static_scale_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'positive static'):
            place(Image.new('RGBA',(4,4)),[0,1],[0,0])
        with self.assertRaisesRegex(ValueError,'positive static'):
            place(Image.new('RGBA',(4,4)),[1,1],[float('nan'),0])
