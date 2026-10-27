"""Camera projection used by the immutable master/source comparison."""
import importlib.util
import math
from pathlib import Path
import unittest
import numpy as np

PATH = Path(__file__).resolve().parents[2] / 'tools/character_factory_v3/review_painted_source_skeleton.py'
SPEC = importlib.util.spec_from_file_location('painted_source_skeleton_review', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PaintedSourceProjectionTest(unittest.TestCase):
    def test_orthographic_center_and_scale(self):
        camera = {'rotation': [0, 0, 0], 'location': [0, 0, 5], 'ortho_scale': 4}
        np.testing.assert_allclose(MODULE.project([0, 0, 0], camera), [384, 384])
        np.testing.assert_allclose(MODULE.project([1, 1, 0], camera), [576, 192])

    def test_camera_roll_uses_local_axes(self):
        camera = {'rotation': [0, 0, math.pi / 2], 'location': [0, 0, 5], 'ortho_scale': 4}
        np.testing.assert_allclose(MODULE.project([0, 1, 0], camera), [576, 384])
        np.testing.assert_allclose(MODULE.project([1, 0, 0], camera), [384, 576])

    def test_depth_does_not_change_orthographic_scale(self):
        camera = {'rotation': [0, 0, 0], 'location': [0, 0, 5], 'ortho_scale': 4}
        np.testing.assert_allclose(MODULE.project([1, 1, 0], camera), MODULE.project([1, 1, -10], camera))


if __name__ == '__main__':
    unittest.main()
