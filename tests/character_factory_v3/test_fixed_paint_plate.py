import sys
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from prepare_fixed_paint_plate import source_union_viewport


class FixedPaintPlateTests(unittest.TestCase):
    def pose(self,box):
        image=Image.new('RGBA',(64,64));image.paste((100,80,60,255),box);return image

    def test_union_includes_extreme_pose_and_snaps_to_author_grid(self):
        viewport,factor=source_union_viewport([self.pose((20,20,30,40)),self.pose((5,7,55,57))],3,32)
        self.assertEqual(viewport,[2,4,58,60]);self.assertEqual(factor,2)

    def test_invalid_author_sizes_are_rejected(self):
        for size in [0,-1,True,3,2.5]:
            with self.subTest(size=size),self.assertRaises(ValueError):source_union_viewport([self.pose((5,5,10,10))],2,size)

    def test_clipped_empty_or_mismatched_sources_are_rejected(self):
        for frames in [[self.pose((0,5,10,10))],[Image.new('RGBA',(64,64))],[self.pose((5,5,10,10)),Image.new('RGBA',(32,32))],[]]:
            with self.subTest(frames=len(frames)),self.assertRaises(ValueError):source_union_viewport(frames,2,32)


if __name__=='__main__':unittest.main()
