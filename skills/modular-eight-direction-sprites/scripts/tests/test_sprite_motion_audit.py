import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[4];SCRIPT=ROOT/'skills/modular-eight-direction-sprites/scripts/sprite-motion-audit.py'
s=importlib.util.spec_from_file_location('motion',SCRIPT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
E=ROOT/'research/sprite-animation/eight-walk-factory-v20/evidence'
B={'max_horizontal_step_px':20,'max_vertical_step_px':8,'max_vertical_range_px':12}

class MotionAuditTests(unittest.TestCase):
 def test_vertical_bounce_is_detected_below_old_total_step_budget(self):
  pts=[[256,y] for y in [100,102,104,102,85,87,89,87]]
  r=m.axis_metrics(pts,[75]*8,True,B)
  self.assertLess(max(np.linalg.norm(x) for x in r['delta_xy_px']),20)
  self.assertTrue(r['warnings']);self.assertTrue(r['vertical_range_warning'])
 def test_loop_seam_is_always_measured(self):
  r=m.axis_metrics([[0,0],[0,1],[0,2],[0,12]],[75]*4,True,B)
  self.assertEqual(r['last_to_first_xy_px'],[0,-12]);self.assertTrue(any(x['to']==0 for x in r['warnings']))
 def test_one_shot_omits_invented_loop_jump(self):
  r=m.axis_metrics([[0,0],[0,1],[0,2],[0,3]],[75]*4,False,B)
  self.assertEqual(len(r['delta_xy_px']),3);self.assertIsNone(r['last_to_first_xy_px'])
 def test_actual_W_residual_bounce_is_not_promoted_by_positive_feedback(self):
  c=json.loads((E/'W-motion-case.json').read_text());c.pop('flow_settings')
  r=m.audit(c);self.assertGreater(r['surface_axis_metrics']['max_vertical_step_px'],8)
  self.assertIn('visible_surface_bounce_or_registration_warning',r['blockers']);self.assertFalse(r['production_ready'])
 def test_actual_stable_front_head_cannot_hide_wrong_lead_pattern(self):
  c=json.loads((E/'S-motion-case.json').read_text());c.pop('flow_settings')
  r=m.audit(c);self.assertEqual(r['status'],'REJECTED');self.assertLess(r['surface_axis_metrics']['max_vertical_step_px'],8)
  self.assertIn('confirmed_actual_image_issue',r['blockers'])
 def test_relabeling_local_flags_does_not_erase_pixel_bound_history(self):
  c=json.loads((E/'S-motion-case.json').read_text());c.pop('flow_settings')
  for f in c['frames']:f['review_issues']=[]
  self.assertEqual(m.audit(c)['status'],'REJECTED')
 def test_changed_pixels_require_reannotation(self):
  c=json.loads((E/'W-motion-case.json').read_text());c['frames'][0]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Changed artwork'):m.audit(c)
 def test_source_phase_relabel_does_not_pass(self):
  c=json.loads((E/'W-motion-case.json').read_text());c['frames'][2]['source_key16']=8
  with self.assertRaisesRegex(ValueError,'Wrong source phase'):m.audit(c)
 def test_color_labels_without_proximal_pixel_evidence_do_not_confirm_anatomy(self):
  c=json.loads((E/'W-motion-case.json').read_text());c['frames'][0]['anatomical_review']['status']='confirmed'
  with self.assertRaisesRegex(ValueError,'anatomical sides|proximal image evidence'):m.audit(c)
 def test_old_unknown_root_and_contact_remain_unknown(self):
  c=json.loads((E/'E-motion-case.json').read_text());c.pop('flow_settings');r=m.audit(c)
  self.assertIn('painted_logical_root_unresolved',r['blockers']);self.assertIn('painted_floor_contacts_unresolved',r['blockers'])
  self.assertIsNone(r['anatomy_accuracy_percent']);self.assertFalse(r['world_support_verified'])
 def test_exposure_time_changes_velocity_without_changing_pixel_steps(self):
  p=[[0,0],[0,2],[0,4],[0,2]];a=m.axis_metrics(p,[50]*4,True,B);b=m.axis_metrics(p,[100]*4,True,B)
  self.assertEqual(a['delta_xy_px'],b['delta_xy_px']);self.assertAlmostEqual(a['velocity_xy_px_s'][0][1],2*b['velocity_xy_px_s'][0][1])
 def test_same_images_flow_is_scoped_not_semantic_pass(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'x.png';a=np.zeros((96,96,4),np.uint8);a[20:76,20:76,:3]=[120,130,180];a[20:76,20:76,3]=255;a[35:55,35:55,:3]=[230,210,190];Image.fromarray(a).save(p)
   r=m.flow_metrics([{'image':str(p)}]*3,True,{'diagnostic_size':96,'max_forward_backward_error_px':1.5,'minimum_consistent_fraction':.5})
   self.assertFalse(r['anatomy_pass']);self.assertTrue(all(x.get('photometric_mae_255',1)<.01 for x in r['edges']))
 def test_invalid_budgets_fail(self):
  with self.assertRaisesRegex(ValueError,'budget'):m.axis_metrics([[0,0]]*3,[75]*3,True,dict(B,max_vertical_step_px=float('nan')))

if __name__=='__main__':unittest.main()
