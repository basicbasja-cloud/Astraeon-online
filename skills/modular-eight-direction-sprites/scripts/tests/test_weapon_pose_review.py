import unittest,json,copy,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];D=ROOT/'research/sprite-animation/weighted-slash-v27';spec=importlib.util.spec_from_file_location('weaponpose',ROOT/'skills/modular-eight-direction-sprites/scripts/weapon-pose-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class WeaponPose(unittest.TestCase):
 def setUp(self):self.c=json.loads((D/'evidence/weapon-pose-case.json').read_text())
 def test_actual_drawn_bank_keeps_camera_foreshortening_but_not_grip_approval(self):
  r=m.audit(self.c,ROOT);self.assertNotIn('drawn_foreshortening_disagrees_with_common_source_scale',r['issues']);self.assertIn('painted_grip_and_occlusion_unverified',r['issues']);self.assertFalse(r['production_pass'])
 def test_runtime_rotation_of_master_is_explicitly_rejected(self):
  self.c['frames'][3]['runtime_rotation_degrees']=35;self.assertIn('flat_weapon_runtime_rotation_forbidden',m.audit(self.c,ROOT)['issues'])
 def test_per_pose_scale_cannot_fake_projection(self):
  self.c['frames'][2]['shared_scale']=2;self.assertIn('per_pose_weapon_rescaling_forbidden',m.audit(self.c,ROOT)['issues'])
 def test_one_flat_master_cannot_replace_changing_projected_lengths(self):
  first=copy.deepcopy(self.c['frames'][0]);self.c['frames']=[{**first,'key':i} for i in range(8)];r=m.audit(self.c,ROOT);self.assertIn('single_flat_master_reused_across_changing_views',r['issues']);self.assertIn('drawn_foreshortening_disagrees_with_common_source_scale',r['issues'])
 def test_changed_pixels_fail_binding(self):
  self.c['frames'][4]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'pixels changed'):m.audit(self.c,ROOT)
if __name__=='__main__':unittest.main()
