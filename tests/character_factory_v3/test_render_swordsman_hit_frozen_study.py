import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import render_swordsman_hit_frozen_study as study
class FrozenHitStudyTests(unittest.TestCase):
 def test_patch_is_opt_in_and_keeps_bone_curves(self):
  original=study.BASE.read_text();patched=study.patched_source(original)
  self.assertIn("if job.get('freeze_source_object_transform'):",patched)
  self.assertIn("fc.data_path in {'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale'}",patched)
  self.assertIn("rig.matrix_world=Matrix.Identity(4)",patched)
 def test_rejects_unrecognized_base(self):
  with self.assertRaises(ValueError):study.patched_source('not the canonical renderer')
if __name__=='__main__':unittest.main()
