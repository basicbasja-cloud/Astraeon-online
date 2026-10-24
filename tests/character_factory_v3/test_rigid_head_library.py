import math
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from review_rigid_head_library import angle_difference,choose_entry,attach_head


class RigidHeadLibraryTests(unittest.TestCase):
    def test_yaw_wrap_does_not_choose_opposite_facing(self):
        entries=[{'index':0,'authored_yaw_degrees':179,'authored_pitch_degrees':0},{'index':1,'authored_yaw_degrees':0,'authored_pitch_degrees':0}]
        self.assertEqual(choose_entry(entries,-179,0)['index'],0)
        self.assertEqual(angle_difference(-179,179),2)

    def test_pitch_selects_the_authored_head_tilt(self):
        entries=[{'index':0,'authored_yaw_degrees':0,'authored_pitch_degrees':-40},{'index':1,'authored_yaw_degrees':0,'authored_pitch_degrees':30}]
        self.assertEqual(choose_entry(entries,2,-35)['index'],0)
        self.assertEqual(choose_entry(entries,2,25)['index'],1)

    def test_translation_is_head_only_and_input_is_unchanged(self):
        source=Image.new('RGBA',(9,9));source.putpixel((4,4),(180,140,100,255));before=np.array(source)
        result=attach_head(source,[4,4],1,0,[20,20],(40,40))
        self.assertEqual(result.getpixel((20,20)),(180,140,100,255))
        np.testing.assert_array_equal(np.array(source),before)
        self.assertEqual(result.getbbox(),(20,20,21,21))

    def test_scale_is_one_uniform_slot_scale(self):
        source=Image.new('RGBA',(12,12),(180,140,100,255));result=attach_head(source,[6,6],.5,0,[20,20],(40,40))
        self.assertEqual(result.getbbox(),(17,17,23,23))
        self.assertEqual(source.size,(12,12))

    def test_invalid_transform_rejected(self):
        source=Image.new('RGBA',(12,12))
        for scale in [0,-1,2,math.nan]:
            with self.assertRaises(ValueError):attach_head(source,[4,4],scale,0,[20,20])
        with self.assertRaises(ValueError):attach_head(source,[4,4],.5,math.inf,[20,20])


if __name__=='__main__':unittest.main()
