import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from build_extended_sword_trail import bounded_path,path_length,paint

class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.points=[(np.array([x,0.]),np.array([x,10.]))for x in [0,10,20]]
    def test_bound_and_fixed_current_tip(self):
        for cap in [1,10,15,20,30]:
            result=bounded_path(self.points,cap)
            self.assertAlmostEqual(path_length(result),min(cap,20))
            np.testing.assert_array_equal(result[-1][1],self.points[-1][1])
            self.assertTrue(all(0<=p[1][0]<=20 for p in result))
    def test_fractional_boundary(self):
        result=bounded_path(self.points,15)
        np.testing.assert_array_equal(result[0][1],np.array([5.,10.]))
    def test_no_extrapolation_at_zero_travel(self):
        same=[self.points[0]]*3
        self.assertEqual(path_length(bounded_path(same,10)),0)
    def test_invalid_bound(self):
        for cap in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):bounded_path(self.points,cap)
    def test_transparent_canvas(self):
        im=paint(self.points)
        self.assertEqual(im.size,(512,512))
        self.assertEqual(im.mode,'RGBA')
        self.assertEqual(im.getpixel((511,511))[3],0)

if __name__=='__main__':unittest.main()
