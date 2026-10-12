import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
loader=importlib.util.spec_from_file_location('ground_contact',Path(__file__).parents[1]/'ground-contact.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)

class GroundContactTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();root=Path(self.temp.name);self.image=root/'foot.png';im=Image.new('RGBA',(32,32));ImageDraw.Draw(im).rectangle((7,8,20,18),fill='white');im.save(self.image)
  blend=root/'synthetic.blend';motion=root/'synthetic-motion.json';blend.write_bytes(b'fixture-not-a-real-rig');motion.write_text('{}')
  self.source=root/'source.json';self.source.write_text(json.dumps({'blend_path':str(blend),'blend_sha256':m.sha(blend),'motion_path':str(motion),'motion_sha256':m.sha(motion),'summary':{'synthetic':True},'frames':[{'soles':{'sole.left.toe':{'minimum_mesh_z':0,'near_plane_candidate':True,'same_xy_on_ground_projected':[10,18],'lowest_xy':[10,18]}}}]}))
  self.spec={'source_ground_path':str(self.source),'source_ground_sha256':m.sha(self.source),'canvas':[32,32],'shared_scale':1,'shared_translation_y_px':0,'warning_budget_px':2,'frames':[{'source_key':0,'image':str(self.image),'sha256':m.sha(self.image),'soles':[{'side':'left','part':'toe','roi_xyxy':[5,6,23,25],'uncertainty_px':1}]}]}
 def tearDown(self):self.temp.cleanup()
 def test_visible_patch_measurement_does_not_claim_support_or_identity(self):
  r=m.audit(self.spec);self.assertFalse(r['contact_warning_keys']);self.assertFalse(r['world_support_verified']);self.assertFalse(r['anatomical_identity_verified']);self.assertFalse(r['art_modified'])
 def test_lower_roi_clip_is_inconclusive(self):
  self.spec['frames'][0]['soles'][0]['roi_xyxy']=[5,6,23,18];r=m.audit(self.spec);self.assertEqual(r['inconclusive_keys'],[0]);self.assertNotIn('contact_floor_warning',r['frames'][0]['observations'][0])
 def test_raised_swing_patch_not_forced_to_ground(self):
  d=json.loads(self.source.read_text());s=d['frames'][0]['soles']['sole.left.toe'];s.update(near_plane_candidate=False,minimum_mesh_z=.1,lowest_xy=[10,4]);self.source.write_text(json.dumps(d));self.spec['source_ground_sha256']=m.sha(self.source)
  o=m.audit(self.spec)['frames'][0]['observations'][0];self.assertFalse(o['contact_floor_warning']);self.assertTrue(o['source_ground_readability_warning'])
 def test_shared_registration_warning_detects_offset(self):
  self.spec['shared_translation_y_px']=10;r=m.audit(self.spec);self.assertEqual(r['contact_warning_keys'],[0]);self.assertFalse(r['per_frame_fit'])
 def test_anchor_is_not_independent_validation(self):
  self.spec['shared_translation_y_px']=10;self.spec['frames'][0]['calibration_sample_not_independent_validation']=True;r=m.audit(self.spec);self.assertEqual(r['contact_warning_keys'],[0]);self.assertFalse(r['independent_contact_warning_keys'])
 def test_changed_art_invalidates_contact_review(self):
  Image.new('RGBA',(32,32),'red').save(self.image)
  with self.assertRaisesRegex(ValueError,'Changed artwork'):m.audit(self.spec)
 def test_changed_source_invalidates_floor_model(self):
  self.source.write_text('{}')
  with self.assertRaisesRegex(ValueError,'Changed source'):m.audit(self.spec)
 def test_negative_phase_key_is_rejected(self):
  self.spec['frames'][0]['source_key']=-1
  with self.assertRaisesRegex(ValueError,'Invalid source phase'):m.audit(self.spec)
 def test_new_character_starts_unknown_and_cannot_approve_contact(self):
  d=m.initialize(self.image.parent,self.source,1,0,2)
  self.assertTrue(all(o['roi_xyxy'] is None for o in d['frames'][0]['soles']))
  r=m.audit(d);self.assertEqual(r['inconclusive_keys'],[0]);self.assertFalse(r['world_support_verified']);self.assertFalse(r['anatomical_identity_verified'])
 def test_new_character_phase_mismatch_and_bad_calibration_rejected(self):
  with self.assertRaisesRegex(ValueError,'transform'):m.initialize(self.image.parent,self.source,float('nan'),0,2)
  Image.new('RGBA',(32,32)).save(self.image.parent/'extra.png')
  with self.assertRaisesRegex(ValueError,'phase count'):m.initialize(self.image.parent,self.source,1,0,2)
 def test_wrong_canvas_rejected(self):
  self.spec['canvas']=[64,64]
  with self.assertRaisesRegex(ValueError,'Wrong artwork canvas'):m.audit(self.spec)
 def test_actual_fractional_source_replay_and_dense_between_key_floor(self):
  root=Path(__file__).resolve().parents[4];d=json.loads((root/'research/sprite-animation/ground-walk-sixteen-v15/source/source-ground.json').read_text())
  self.assertEqual(len(d['frames']),16);self.assertEqual(len(d['dense_samples']),129);self.assertAlmostEqual(d['frames'][1]['source_sample_position'],2.5)
  self.assertEqual(d['summary']['both_feet_airborne_candidates'],0);self.assertGreater(d['summary']['minimum_sole_z'],-.002);self.assertFalse(d['source_pose_edited'])
  for f in d['dense_samples']:
   self.assertTrue(any(s['near_plane_candidate'] for s in f['soles'].values()))
   for s in f['soles'].values():self.assertEqual(s['same_xy_on_ground_world'][2],0)
 def test_actual_oblique_ground_is_not_one_horizontal_foot_line(self):
  root=Path(__file__).resolve().parents[4];d=json.loads((root/'research/sprite-animation/ground-walk-sixteen-v15/source/source-ground.json').read_text());s=d['frames'][0]['soles'];left=s['sole.left.heel']['same_xy_on_ground_projected'][1];right=s['sole.right.heel']['same_xy_on_ground_projected'][1];self.assertGreater(left-right,15)
 def test_actual_old_and_new_contact_warnings_remain_diagnostic(self):
  root=Path(__file__).resolve().parents[4];ev=root/'research/sprite-animation/ground-walk-sixteen-v15/evidence'
  old=m.audit(json.loads((ev/'v14-ground-observations.json').read_text()));new=m.audit(json.loads((ev/'v15-ground-observations.json').read_text()))
  self.assertIn(8,old['contact_warning_keys']);self.assertTrue(new['independent_contact_warning_keys']);self.assertFalse(new['world_support_verified'])
if __name__=='__main__':unittest.main()
