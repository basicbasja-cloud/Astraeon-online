import sys
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_locomotion_kit import split_leg
from build_occluded_underlays import composite
from render_articulated_native_action import paint_affine


class ArticulatedNativeTests(unittest.TestCase):
    def test_leg_split_preserves_soft_edges_and_native_joint_underlap(self):
        a=np.zeros((40,20,4),np.uint8);a[2:36,5:15]=[90,60,30,255];a[2:36,5]=[90,60,30,128]
        im=Image.fromarray(a);parts=split_leg(im,'L',{'Shin.L':[10,15],'Foot.L':[10,31]},2)
        self.assertEqual(composite(list(parts.values())).tobytes(),im.tobytes())
        self.assertTrue(all(np.array(p)[:,:,3].any()for p in parts.values()))
    def test_premultiplied_affine_retains_shape_and_transparent_background(self):
        a=Image.new('RGBA',(16,16));a.paste((90,60,30,255),(4,4,8,8))
        b=paint_affine(a,np.array([[1.,0,3],[0,1.,2]]))
        self.assertEqual(b.getpixel((7,6)),(90,60,30,255));self.assertEqual(b.getpixel((4,4)),(0,0,0,0))
