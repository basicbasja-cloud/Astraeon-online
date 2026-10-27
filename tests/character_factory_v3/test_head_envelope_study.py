import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from build_head_envelope_study import fit_head,derive
class HeadEnvelopeTests(unittest.TestCase):
 def test_zero_influence_positions_unchanged(self):
  p=np.array([[0.,0,0],[1,2,0],[2,3,1]],dtype=np.float32);r,c=fit_head(p,[0,1,1],1.3);np.testing.assert_array_equal(r[0],p[0]);self.assertFalse(np.array_equal(r[1:],p[1:]))
 def test_unbounded_or_missing_head_cannot_fit(self):
  with self.assertRaises(ValueError):fit_head(np.zeros((2,3)),[0,0],1.3)
  with self.assertRaises(ValueError):fit_head(np.zeros((2,3)),[1,1],2)
 def test_real_glb_motion_and_feet_preserved(self):
  source=ROOT/'authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb';raw,r=derive(source,1.3);self.assertTrue(r['animation_and_skeleton_json_unchanged']);self.assertTrue(r['foot_positions_unchanged']);self.assertGreater(r['changed_position_vertices'],0);self.assertGreater(len(raw),1000)
