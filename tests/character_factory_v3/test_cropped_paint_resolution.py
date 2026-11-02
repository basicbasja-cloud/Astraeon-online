import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from qualify_cropped_paint_resolution import qualify


class CroppedResolutionTests(unittest.TestCase):
    def test_zoomed_crop_downsamples_into_768_canvas(self):
        result=qualify([1448,1086],[4,3],[1536,1536],[448,520,1088,1160],[768,768])
        self.assertEqual(result['canonical_viewport'],[224,260,544,580])
        self.assertEqual(result['canonical_viewport_size'],[320,320])
        self.assertEqual(result['native_pixels_per_authoring_pixel_xy'],[1.13125,1.13125])
        self.assertTrue(result['native_resolution_sufficient']);self.assertFalse(result['requires_upsampling'])
        self.assertFalse(result['anatomy_or_contact_approved'])

    def test_same_native_slot_is_insufficient_for_a_full_frame(self):
        result=qualify([1448,1086],[4,3],[1536,1536],[0,0,1536,1536],[768,768])
        self.assertFalse(result['native_resolution_sufficient']);self.assertTrue(result['requires_upsampling'])

    def test_nonuniform_and_invalid_contracts_are_rejected(self):
        for sheet,grid,crop,canvas in [([1448,1000],[4,3],[448,520,1088,1160],[768,768]),
            ([1448,1086],[4,3],[448,520,1088,1160],[768,512]),
            ([1448,1086],[True,3],[448,520,1088,1160],[768,768]),
            ([1448,1086],[4,3],[-1,520,1088,1160],[768,768])]:
            with self.subTest(sheet=sheet,grid=grid,crop=crop,canvas=canvas):
                with self.assertRaises(ValueError):qualify(sheet,grid,[1536,1536],crop,canvas)

    def test_exact_detail_and_fractional_cell_boundaries_are_reported(self):
        result=qualify([1280,960],[4,3],[1536,1536],[448,520,1088,1160],[768,768])
        self.assertTrue(result['native_resolution_sufficient']);self.assertEqual(result['native_pixels_per_authoring_pixel_xy'],[1,1])
        result=qualify([1281,960],[4,3],[1536,1536],[448,520,1088,1160],[768,768])
        self.assertEqual(result['raw_slot_size'],[320.25,320])

if __name__=='__main__':unittest.main()
