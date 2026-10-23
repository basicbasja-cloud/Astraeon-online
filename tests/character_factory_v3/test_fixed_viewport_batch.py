import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from normalize_fixed_viewport_batch import normalize_batch, unmatte_white_edges


class FixedViewportBatchTests(unittest.TestCase):
    def recipe(self):
        return {'grid': [2, 2], 'source_size': [40, 40], 'viewport': [8, 4, 24, 36],
                'source_pose_indices': [4, 5, 6, 7]}

    def test_rectangular_cells_keep_absolute_source_positions(self):
        sheet = Image.new('RGBA', (32, 64))
        for i in range(4):
            sheet.putpixel((i % 2*16+3+i, i//2*32+10), (50, 30, 10, 255))
        frames, receipt = normalize_batch(sheet, self.recipe())
        for i, frame in enumerate(frames):
            self.assertEqual(frame.getbbox(), (11+i, 14, 12+i, 15))
        self.assertFalse(receipt['runtime_admitted'])
        self.assertFalse(receipt['per_frame_figure_fitting'])

    def test_reject_aspect_drift_instead_of_stretching(self):
        with self.assertRaisesRegex(ValueError, 'do not stretch'):
            normalize_batch(Image.new('RGBA', (64, 64)), self.recipe())

    def test_fractional_grid_has_one_shared_cell_extent(self):
        recipe = {'grid': [2, 2], 'source_size': [40, 40], 'viewport': [4, 4, 36, 36],
                  'source_pose_indices': [0, 1, 2, 3]}
        _, receipt = normalize_batch(Image.new('RGBA', (65, 65)), recipe)
        self.assertEqual({r['source_box'][2]-r['source_box'][0] for r in receipt['frames']}, {32.5})

    def test_preserve_enclosed_ivory_and_real_transparency(self):
        sheet = Image.new('RGBA', (32, 64), 'white')
        draw = ImageDraw.Draw(sheet)
        for i in range(4):
            x, y = i % 2*16, i//2*32
            draw.rectangle((x+2, y+2, x+13, y+29), fill='#403020')
            draw.rectangle((x+3, y+3, x+12, y+28), fill='#fafaf5')
        frames, _ = normalize_batch(sheet, self.recipe())
        self.assertEqual(frames[0].getpixel((12, 8)), (250, 250, 245, 255))
        self.assertEqual(frames[0].getpixel((8, 4)), (0, 0, 0, 0))
        sheet = Image.new('RGBA', (32, 64), (250, 250, 245, 150))
        frames, _ = normalize_batch(sheet, self.recipe())
        self.assertEqual(frames[0].getpixel((8, 4)), (250, 250, 245, 150))

    def test_reject_duplicate_pose_or_outside_viewport(self):
        recipe = self.recipe(); recipe['source_pose_indices'] = [0, 0, 2, 3]
        with self.assertRaises(ValueError): normalize_batch(Image.new('RGBA', (32, 64)), recipe)

    def test_white_unmatting_recovers_soft_edge_and_protects_interior(self):
        a = np.full((16, 16, 4), 255, dtype=np.uint8)
        a[4:12, 4:12, :3] = [30, 20, 10]
        a[3, 4:12, :3] = [165, 161, 157]  # approximately 40% paint over white
        background = np.all(a[:, :, :3] == 255, axis=2)
        out, count = unmatte_white_edges(a, background)
        self.assertGreater(count, 0)
        self.assertLess(out[3, 8, 3], 120)
        self.assertLess(out[3, 8, :3].max(), 40)
        np.testing.assert_array_equal(out[6:10, 6:10], a[6:10, 6:10])
        recovered = out[3, 8, :3]* (out[3, 8, 3]/255) + 255*(1-out[3, 8, 3]/255)
        self.assertLessEqual(np.abs(recovered-a[3, 8, :3]).max(), 1)

    def test_white_unmatting_does_not_reprocess_existing_alpha(self):
        sheet = Image.new('RGBA', (32, 64), (250, 250, 245, 150))
        frames, _ = normalize_batch(sheet, self.recipe(), white_edge_unmatting=True)
        self.assertEqual(frames[0].getpixel((8, 4)), (250, 250, 245, 150))
        recipe = self.recipe(); recipe['viewport'][2] = 41
        with self.assertRaises(ValueError): normalize_batch(Image.new('RGBA', (32, 64)), recipe)


if __name__ == '__main__':
    unittest.main()
