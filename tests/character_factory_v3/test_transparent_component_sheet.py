import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from extract_transparent_component_sheet import extract


class TransparentComponentSheetTests(unittest.TestCase):
    def sheet(self):
        pixels = np.zeros((64, 128, 4), dtype=np.uint8)
        pixels[8:48, 20:56] = [100, 60, 30, 213]
        pixels[44:50, 45:70] = [80, 40, 20, 199]  # Boot spills past column 64.
        pixels[8:49, 92:118] = [30, 80, 120, 254]
        return Image.fromarray(pixels)

    def test_whole_boot_is_not_cut_at_a_grid_boundary(self):
        frames, receipt = extract(self.sheet(), [2, 1], [128, 128], [32, 32], minimum_figure_area=100)
        self.assertEqual(frames[0].getpixel((99, 78)), (80, 40, 20, 199))
        self.assertEqual(frames[1].getpixel((35, 78))[3], 0)
        self.assertGreater(receipt['spill_pixels_preserved'], 0)
        self.assertEqual(receipt['assigned_pixel_recomposition_mismatches'], 0)
        self.assertFalse(receipt['per_figure_scaling_or_fitting'])

    def test_a_merged_pair_cannot_silently_become_one_sprite(self):
        pixels = np.array(self.sheet())
        pixels[20:30, 50:100] = [80, 50, 30, 255]
        with self.assertRaisesRegex(ValueError, 'separate whole figures'):
            extract(Image.fromarray(pixels), [2, 1], [128, 128], [32, 32], minimum_figure_area=100)

    def test_small_output_canvas_is_rejected_without_scaling(self):
        with self.assertRaisesRegex(ValueError, 'clips'):
            extract(self.sheet(), [2, 1], [32, 32], [0, 0], minimum_figure_area=100)

    def test_fractional_grid_stride_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'integer grid'):
            extract(self.sheet(), [3, 1], [128, 128], [32, 32], minimum_figure_area=100)


if __name__ == '__main__':
    unittest.main()
