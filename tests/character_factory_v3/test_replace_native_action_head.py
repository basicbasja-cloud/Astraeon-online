import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from replace_native_action_head import validate_rigid


class RigidHeadVariantTests(unittest.TestCase):
    def test_rotation_and_translation_are_accepted(self):
        a=.4;m=np.array([[np.cos(a),-np.sin(a),18],[np.sin(a),np.cos(a),-4]])
        np.testing.assert_equal(validate_rigid(m),m)
    def test_scale_shear_and_reflection_cannot_change_a_replacement_head(self):
        for m in [[[1.01,0,0],[0,1,0]],[[1,.1,0],[0,1,0]],[[-1,0,0],[0,1,0]]]:
            with self.assertRaisesRegex(ValueError,'stretched or reflected'):validate_rigid(m)
