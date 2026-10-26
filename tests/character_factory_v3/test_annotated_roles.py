import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from propose_annotated_roles import partition,composite,faint_edges


class AnnotatedRoleTests(unittest.TestCase):
    def test_invisible_rgb_is_canonicalized_without_changing_any_visible_pixel(self):
        image=Image.new('RGBA',(8,8));image.putpixel((1,1),(80,40,20,0));image.putpixel((2,2),(90,60,30,128));mask=np.zeros((8,8),bool);mask[2,2]=True
        parts,_=partition(image,{'HeadHair':mask},['HeadHair']);actual=composite(list(parts.values()))
        self.assertEqual(actual.getpixel((1,1)),(0,0,0,0));self.assertEqual(actual.getpixel((2,2)),(90,60,30,128))
    def test_edge_ownership_reclaims_only_nearby_soft_source_pixels(self):
        mask=np.zeros((12,12),bool);mask[5,5]=True;alpha=np.zeros((12,12),np.uint8);alpha[5,5]=255;alpha[5,6]=128;alpha[5,7]=255;alpha[0,0]=128
        result=faint_edges(mask,alpha)
        self.assertTrue(result[5,6]);self.assertFalse(result[5,7]);self.assertFalse(result[0,0])
    def test_semantic_priority_retains_source_soft_edges_exactly_once(self):
        image=Image.new('RGBA',(8,8),(90,60,30,128));head=np.zeros((8,8),bool);head[:4,:4]=True;hand=head.copy();hand[:2]=False
        parts,labels=partition(image,{'HeadHair':head,'WeaponHandOccluder':hand},['HeadHair','WeaponHandOccluder'])
        self.assertEqual(composite(list(parts.values())).tobytes(),image.tobytes())
        self.assertEqual(labels[3,3],2);self.assertEqual(parts['HeadHair'].getpixel((3,3)),(0,0,0,0))
    def test_missing_role_priority_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'priority'):partition(Image.new('RGBA',(8,8)),{'HeadHair':np.zeros((8,8),bool)},[])
