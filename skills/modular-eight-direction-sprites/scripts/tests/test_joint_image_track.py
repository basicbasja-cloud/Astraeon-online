import importlib.util, json, tempfile, unittest
from pathlib import Path
import cv2, numpy as np
from PIL import Image
SCRIPTS=Path(__file__).resolve().parents[1]
def module(name):
 s=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('joint-image-track');R=module('joint-track-reference-review');D=module('pose-image-proposals')
class TrackTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  rng=np.random.default_rng(17);rgb=rng.integers(0,255,(96,96,3),dtype=np.uint8)
  self.images=[];self.case={'schema':'sprite-image-joint-tracks-v1','canvas':[96,96],'frames':[],'seeds':[],'source_sha256':'source','thresholds':{'levels':1}}
  for i in range(5):
   im=np.dstack((cv2.warpAffine(rgb,np.float32([[1,0,i*2],[0,1,i]]),(96,96)),np.full((96,96),255,np.uint8)))
   path=self.root/f'{i}.png';Image.fromarray(im).save(path)
   self.case['frames'].append({'path':path.name,'sha256':M.sha(path),'time_ms':i*75,'duration_ms':75})
  self.seed(0,'right.knee',[40,40]);self.path=self.root/'case.json';self.save()
 def tearDown(self):self.tmp.cleanup()
 def seed(self,f,j,xy,kind='manual_visible'):
  self.case['seeds'].append({'frame':f,'joint':j,'xy':xy,'image_sha256':self.case['frames'][f]['sha256'],'kind':kind,'uncertainty_px':1,'owner_confirmed':True})
 def save(self):self.path.write_text(json.dumps(self.case))
 def loaded(self):self.save();return M.load_case(self.path,self.root)
 def test_actual_pixel_translation(self):
  c,im=self.loaded();r=M.track(c,im)
  for i in range(1,5):
   p=r['frames'][i]['points']['right.knee'];self.assertEqual(p['status'],'proposal');self.assertLess(np.linalg.norm(np.array(p['xy'])-[40+2*i,40+i]),.1);self.assertFalse(p['anatomical_identity_verified'])
  self.assertFalse(r['anatomy_pass']);self.assertFalse(r['production_pass'])
 def test_textureless_abstention(self):
  blank={'gray':np.zeros((96,96),np.uint8),'rgba':np.full((96,96,4),255,np.uint8)}
  self.assertEqual(M.correspondence(blank,blank,[40,40],M.DEFAULTS)['status'],'unknown')
 def test_unknown_stops_then_explicit_seed_restarts(self):
  self.case['explicit_unknowns']=[{'frame':1,'joint':'right.knee','image_sha256':self.case['frames'][1]['sha256']}]
  self.seed(3,'right.knee',[46,43]);c,im=self.loaded();r=M.track(c,im)
  self.assertEqual([f['points']['right.knee']['status'] for f in r['frames']],['seed','unknown','unknown','seed','proposal'])
 def test_stale_pixels_refused(self):
  Image.new('RGBA',(96,96),'red').save(self.root/'1.png')
  with self.assertRaisesRegex(ValueError,'Changed image'):self.loaded()
 def test_stale_seed_refused(self):
  self.case['seeds'][0]['image_sha256']='stale'
  with self.assertRaisesRegex(ValueError,'Stale seed'):self.loaded()
 def test_hidden_coordinate_cannot_seed(self):
  self.case['seeds'][0]['kind']='estimated'
  with self.assertRaisesRegex(ValueError,'cannot seed'):self.loaded()
 def test_clock_and_canvas_refused(self):
  self.case['frames'][2]['time_ms']=200
  with self.assertRaisesRegex(ValueError,'clock'):self.loaded()
 def test_proposal_collision_never_renames_owner(self):
  self.seed(0,'left.knee',[41,40]);c,im=self.loaded();r=M.track(c,im)
  for j in ('right.knee','left.knee'):self.assertEqual(r['frames'][1]['points'][j]['status'],'untrusted')
  self.assertEqual(r['frames'][0]['points']['right.knee']['xy'],[40,40])
 def test_assisted_requires_backtracking_discloses_seed_truth(self):
  self.case['seeds'][0]['kind']='source_projected_benchmark';self.seed(4,'right.knee',[48,44],'source_projected_benchmark');c,im=self.loaded();r=M.bidirectional(c,im)
  self.assertTrue(r['future_reference_coordinates_used']);self.assertFalse(r['future_unseeded_truth_used']);self.assertEqual(r['labelled_seed_frames'],[0,4])
  self.assertEqual(r['frames'][2]['points']['right.knee']['status'],'proposal');self.assertFalse(r['anatomy_pass'])
class ReferenceTests(unittest.TestCase):
 def fixture(self,x=10,left=30):
  tr={'reference_source_sha256':'source','frames':[{'index':0,'image_sha256':'image','reference_time_seconds':0,'points':{'right.knee':{'xy':[x,10],'status':'proposal'},'grip':{'xy':None,'status':'unknown'}}}]}
  gt={'source_sha256':'source','frames':[{'index':0,'candidate_image_sha256':'image','source_time_seconds':0,'points':{'right.knee':{'xy':[10,10]},'left.knee':{'xy':[left,10]}}}]};return tr,gt
 def test_swapped_reference_flags_but_never_renames(self):
  tr,gt=self.fixture(30);r=R.audit(tr,gt);self.assertEqual(r['issues'][0]['status'],'POSSIBLE_OWNER_OR_POSE_MISMATCH');self.assertFalse(r['automatic_owner_labels_changed'])
 def test_overlap_is_ambiguous_even_perfect_match(self):
  tr,gt=self.fixture(left=12);self.assertEqual(R.audit(tr,gt)['issues'][0]['status'],'OWNER_AMBIGUOUS_AT_OVERLAP')
 def test_missing_point_is_reported_not_silently_passed(self):
  tr,gt=self.fixture();gt['frames'][0]['points']['grip']={'xy':[10,10]};r=R.audit(tr,gt);self.assertIn('TRACK_UNAVAILABLE',[i['status'] for i in r['issues']]);self.assertFalse(r['anatomy_pass'])
 def test_stale_source_and_candidate_refused(self):
  tr,gt=self.fixture();gt['source_sha256']='other'
  with self.assertRaises(ValueError):R.audit(tr,gt)
  gt['source_sha256']='source';gt['frames'][0]['candidate_image_sha256']='changed'
  with self.assertRaises(ValueError):R.audit(tr,gt)
 def test_mismatched_phase_refused(self):
  tr,gt=self.fixture();gt['frames'][0]['source_time_seconds']=.5
  with self.assertRaisesRegex(ValueError,'phase'):R.audit(tr,gt)
class ModelCoordinateTests(unittest.TestCase):
 def test_inverse_coordinates_not_crop_coordinates_or_probability(self):
  class Net:
   def setInput(self,x):pass
   def getUnconnectedOutLayersNames(self):return ['x','y']
   def forward(self,x):
    a=np.zeros((1,133,576),np.float32);b=np.zeros((1,133,768),np.float32);a[:,:,288]=2;b[:,:,384]=2;return a,b
  r=D.infer(Net(),np.full((200,100,4),255,np.uint8));p=r['points']['right.knee'];self.assertEqual(p['xy'],[50,100]);self.assertFalse(p['score_is_accuracy_probability']);self.assertFalse(r['production_pass'])
if __name__=='__main__':unittest.main()
