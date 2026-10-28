import importlib.util
from pathlib import Path
import unittest
import numpy as np
from PIL import Image

PATH = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/project_filtered_part_coverage.py'
SPEC = importlib.util.spec_from_file_location('filtered_part_coverage', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FilteredPartCoverageTest(unittest.TestCase):
    def setUp(self):
        pixels = np.zeros((64, 64, 4), dtype='uint8')
        pixels[12:50, 12:50] = [180, 80, 40, 253]
        self.image = Image.fromarray(pixels)
        self.mask = np.zeros((64, 64), bool)
        self.mask[12:50, 12:33] = True
        self.args = ([32, 32, 96, 96], .83, [8.4, 4.2], [0, 0])

    def test_support_matches_actual_filtered_isolated_rgba_part(self):
        actual = MODULE.project_coverage(self.image, self.mask, *self.args, canvas_size=(128, 128))
        p = np.array(self.image)
        p[~self.mask] = 0
        canvas = Image.new('RGBA', (128, 128))
        canvas.alpha_composite(Image.fromarray(p), (32, 32))
        expected = canvas.convert('RGBa').transform((128, 128), Image.Transform.AFFINE,
                    (1/.83, 0, -8.4/.83, 0, 1/.83, -4.2/.83), Image.Resampling.BICUBIC).convert('RGBA')
        np.testing.assert_array_equal(actual, np.array(expected)[:, :, 3] > 0)

    def test_nearest_mask_misses_actual_edge_support(self):
        actual = MODULE.project_coverage(self.image, self.mask, *self.args, canvas_size=(128, 128))
        nearest = Image.new('L', (128, 128))
        nearest.paste(Image.fromarray(self.mask.astype('uint8')*255), (32, 32))
        nearest = nearest.transform((128, 128), Image.Transform.AFFINE,
                    (1/.83, 0, -8.4/.83, 0, 1/.83, -4.2/.83), Image.Resampling.NEAREST)
        self.assertGreater(np.count_nonzero(actual & ~(np.array(nearest) > 0)), 0)

    def test_integer_registration_and_source_immutability(self):
        before = self.image.tobytes()
        reference = MODULE.project_coverage(self.image, self.mask, *self.args, canvas_size=(128, 128))
        shifted = MODULE.project_coverage(self.image, self.mask, *self.args[:3], [3, -2], canvas_size=(128, 128))
        expected = np.zeros_like(reference)
        expected[:-2, 3:] = reference[2:, :-3]
        np.testing.assert_array_equal(shifted, expected)
        self.assertEqual(self.image.tobytes(), before)

    def test_opaque_unprocessed_matte_rejected(self):
        with self.assertRaisesRegex(ValueError, 'matte preprocessing'):
            MODULE.project_coverage(Image.new('RGBA', (64, 64), 'white'), self.mask, *self.args)

    def test_wrong_mask_shape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'native boolean'):
            MODULE.project_coverage(self.image, np.zeros((32, 32), bool), *self.args)

    def test_shared_fit_clipping_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Shared fit would clip'):
            MODULE.project_coverage(self.image, self.mask, self.args[0], 20, [0, 0], [0, 0], canvas_size=(128, 128))

    def test_fractional_registration_rejected(self):
        with self.assertRaisesRegex(ValueError, 'integer translation'):
            MODULE.project_coverage(self.image, self.mask, *self.args[:3], [.5, 0])


if __name__ == '__main__':
    unittest.main()
