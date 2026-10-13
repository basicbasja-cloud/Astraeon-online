import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
S=Path(__file__).resolve().parents[1]
def mod(name):
 s=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=mod('planted-surface-review');T=mod('image-surface-track')
class SurfaceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.case={'schema':'sprite-image-joint-tracks-v1','canvas':[64,64],'surface_landmarks':{'surface.toe':{'definition':'visible toe-cap surface','anatomical_owner':'unknown','policy':'planted_surface_proxy'}},'planted_budget_px':6,'frames':[],'seeds':[]}
  for i in range(3):
   f=self.root/f'{i}.png';Image.new('RGBA',(64,64),'white').save(f);h=hashlib.sha256(f.read_bytes()).hexdigest();self.case['frames'].append({'path':f.name,'sha256':h,'time_ms':i*100,'duration_ms':100,'source_time_seconds':i*.1,'observations':{'surface.toe':{'status':'visible','xy':[20,40],'uncertainty_px':3}}})
 def tearDown(self):self.tmp.cleanup()
 def test_static_visible_surface_does_not_approve_contact_anatomy(self):
  r=M.audit(self.case,self.root);self.assertTrue(r['numerical_surface_check_pass']);self.assertFalse(r['contact_pass']);self.assertFalse(r['anatomy_pass']);self.assertFalse(r['production_pass'])
 def test_horizontal_slide_caught_even_when_height_unchanged(self):
  self.case['frames'][1]['observations']['surface.toe']['xy']=[35,40];r=M.audit(self.case,self.root);self.assertEqual(r['issues'][0]['kind'],'PLANTED_SURFACE_DRIFT');self.assertEqual(r['issues'][0]['range_xy_px'],[15,0])
 def test_unknown_surface_is_not_guessed(self):
  self.case['frames'][1]['observations']['surface.toe']={'status':'unknown'};self.assertIn('UNKNOWN_SURFACE',[i['kind'] for i in M.audit(self.case,self.root)['issues']])
 def test_changed_image_is_refused(self):
  Image.new('RGBA',(64,64),'red').save(self.root/'0.png')
  with self.assertRaises(ValueError):M.audit(self.case,self.root)
 def test_clock_drift_refused(self):
  self.case['frames'][1]['time_ms']=150
  with self.assertRaisesRegex(ValueError,'clock'):M.audit(self.case,self.root)
 def test_surface_adapter_never_infers_hidden_joint_or_owner(self):
  self.case['seeds']=[{'frame':0,'joint':'surface.toe','xy':[20,40],'image_sha256':self.case['frames'][0]['sha256'],'kind':'manual_visible','owner_confirmed':False}]
  p=self.root/'case.json';p.write_text(json.dumps(self.case));c,r,m=T.run(p,self.root);self.assertEqual(r['frames'][0]['points']['right.knee']['status'],'unknown');self.assertFalse(r['frames'][0]['points']['surface.toe']['anatomical_identity_verified']);self.assertFalse(r['hidden_joint_coordinates_inferred'])
 def test_joint_estimate_cannot_seed_surface_adapter(self):
  self.case['seeds']=[{'frame':0,'joint':'right.knee','xy':[20,40]}];p=self.root/'case.json';p.write_text(json.dumps(self.case))
  with self.assertRaisesRegex(ValueError,'cannot seed'):T.run(p,self.root)
 def test_surface_owner_confirmation_cannot_approve_joint(self):
  self.case['seeds']=[{'frame':0,'joint':'surface.toe','xy':[20,40],'owner_confirmed':True}];p=self.root/'case.json';p.write_text(json.dumps(self.case))
  with self.assertRaisesRegex(ValueError,'cannot certify'):T.run(p,self.root)
 def phase_case(self):
  for i,y in enumerate((20,50,22)):self.case['frames'][i]['observations']['surface.toe']['xy']=[20,y]
  self.case['surface_landmarks']['surface.toe']['policy']='moving_surface'
  src=self.root/'source.json';src.write_text(json.dumps({'frames':[{'source_time_seconds':i*.1,'points':{'right.wrist':{'xy':[0,y]}}} for i,y in enumerate((0,30,20))]}))
  self.case['reference_phase']={'source_file':'source.json','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'marker':'surface.toe','source_joint':'right.wrist','axis':1,'calibration_frames':[0,1],'warning_fraction':.25}
  return src
 def test_early_recovery_caught_excluding_calibration_points(self):
  self.phase_case();r=M.audit(self.case,self.root);issues=[i for i in r['issues'] if i['kind']=='SOURCE_RELATIVE_PHASE_DISAGREEMENT'];self.assertEqual([i['frame'] for i in issues],[2]);self.assertFalse(r['anatomy_pass'])
 def test_changed_phase_source_refused(self):
  p=self.phase_case();p.write_text('{}')
  with self.assertRaisesRegex(ValueError,'phase reference'):M.audit(self.case,self.root)
 def test_occluded_phase_calibration_is_unknown_not_crash(self):
  self.phase_case();self.case['frames'][0]['observations'].clear();r=M.audit(self.case,self.root);self.assertIn('INSUFFICIENT_PHASE_EXCURSION',[i['kind'] for i in r['issues']])
if __name__=='__main__':unittest.main()
