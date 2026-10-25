import importlib.util
from pathlib import Path
import unittest

import numpy as np
from PIL import Image, ImageDraw

PATH = Path(__file__).resolve().parents[2]/'tools/character_factory_v3/audit_staff_motion.py'
spec = importlib.util.spec_from_file_location('staff_motion', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StaffMotionAuditTests(unittest.TestCase):
    def test_orthographic_projection_flips_vertical_canvas_axis(self):
        camera={'location':[0,0,0],'rotation':[0,0,0],'ortho_scale':2}
        np.testing.assert_allclose(module.project([.5,.25,-5],camera,100),[75,37.5])

    def test_projection_uses_camera_rotation(self):
        camera={'location':[0,0,0],'rotation':[0,0,np.pi/2],'ortho_scale':2}
        np.testing.assert_allclose(module.project([0,.5,-5],camera,100),[75,50],atol=1e-10)

    def test_largest_visible_upper_crystal_is_measured(self):
        image=Image.new('RGBA',(100,150))
        draw=ImageDraw.Draw(image)
        draw.rectangle((20,10,29,19),fill=(10,160,210,255))
        draw.rectangle((60,20,62,22),fill=(10,160,210,255))
        draw.rectangle((50,100,90,140),fill=(10,160,210,255))
        draw.rectangle((40,25,80,50),fill=(10,160,210,0))
        center,area=module.observed_crystal(image,100)
        np.testing.assert_allclose(center,[24.5,14.5])
        self.assertEqual(area,100)

    def test_missing_crystal_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,'Missing observed'):
            module.observed_crystal(Image.new('RGBA',(100,100)),90)


if __name__ == '__main__':
    unittest.main()
