import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from paint_cutout_sword_trail import blade_axis,bounded_history,ribbon


class SwordCutoutTrailTests(unittest.TestCase):
    def test_blade_ends_follow_painted_pixels(self):
        image=Image.new('RGBA',(128,128));ImageDraw.Draw(image).line([(20,20),(100,50)],fill=(190,190,210,255),width=3)
        base,tip=blade_axis(image,np.array([105,52]));self.assertLess(np.linalg.norm(base-[100,50]),3);self.assertLess(np.linalg.norm(tip-[20,20]),3)

    def test_recent_tip_travel_is_bounded_and_ends_on_actual_blade(self):
        history=[(np.array([0.,0.]),np.array([0.,-100.])),(np.array([0.,0.]),np.array([100.,0.])),(np.array([0.,0.]),np.array([0.,100.]))]
        base=np.array([80.,80.]);tip=np.array([80.,120.]);selected,travel,cap=bounded_history(history,base,tip)
        self.assertLessEqual(travel,22.+1e-8);self.assertEqual(cap,22.);np.testing.assert_allclose(selected[-1][0],base);np.testing.assert_allclose(selected[-1][1],tip)
        self.assertIsNotNone(ribbon(selected,160).getbbox())

    def test_long_or_degenerate_history_is_rejected(self):
        history=[(np.array([0.,0.]),np.array([0.,1.]))]
        with self.assertRaises(ValueError):bounded_history(history,np.array([1.,1.]),np.array([2.,2.]))
        with self.assertRaises(ValueError):bounded_history(history,np.array([1.,1.]),np.array([20.,20.]),1.)


if __name__=='__main__':unittest.main()
