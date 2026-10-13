"""Negative production faults must survive positive numerical/rig receipts."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];S=ROOT/'skills/modular-eight-direction-sprites/scripts';P=ROOT/'research/sprite-animation/pickup-modular-v32'
def load(n,file):
 s=importlib.util.spec_from_file_location(n,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
observer=load('obs',S/'rigged-surface-observer.py');review=load('review',S/'modular-motion-review.py');surface=load('surface',S/'planted-surface-review.py')
class ReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.observercase=json.loads((P/'observer-case.json').read_text());cls.frames=[observer.read_bound(ROOT,r) for r in cls.observercase['frames']]
 def test_actual_held_out_pixels_match_rig_only_after_tracking(self):
  r=observer.observe(self.observercase,ROOT);poses=json.loads((P/'poses.json').read_text());dist=[np.linalg.norm(np.array(p['xy'])-poses[i]['joints']['right.wrist']) for i,p in enumerate(r['tracks']['surface.reaching_cuff']) if i>0]
  self.assertLess(max(dist),1);self.assertFalse(r['later_pose_coordinates_used']);self.assertFalse(r['hidden_anatomy_detected'])
 def test_image_translation_detects_support_drift(self):
  frames=[a.copy() for a in self.frames];frames[5][:]=0;frames[5][:,12:]=self.frames[5][:,:-12]
  for name in ('surface.far_boot_toe','surface.near_boot_toe'):
   tracks=observer.match(frames,self.observercase['patches'][name]);self.assertTrue(all(p['status']=='visible' for p in tracks));self.assertGreater(np.ptp([p['xy'][0] for p in tracks]),6)
 def test_blank_or_occluded_texture_abstains(self):
  frames=[a.copy() for a in self.frames];frames[4][:]=0
  tracks=observer.match(frames,self.observercase['patches']['surface.far_boot_toe']);self.assertEqual(tracks[4]['status'],'unknown');self.assertIsNone(tracks[4]['xy'])
 def test_stale_image_hash_refused(self):
  case=copy.deepcopy(self.observercase);case['frames'][4]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Changed'):observer.observe(case,ROOT)
 def test_duplicate_texture_is_ambiguous(self):
  frames=[a.copy() for a in self.frames];frames[6][457:474,138:159]=frames[0][457:474,108:129]
  tracks=observer.match(frames,self.observercase['patches']['surface.far_boot_toe']);self.assertEqual(tracks[6]['status'],'unknown');self.assertLess(tracks[6]['position_margin'],.015)
 def test_texture_free_seed_refused(self):
  blank=[np.zeros_like(self.frames[0]) for _ in range(8)]
  with self.assertRaisesRegex(ValueError,'Insufficient'):observer.match(blank,self.observercase['patches']['surface.far_boot_toe'])
 def test_old_whole_sheet_failures_still_fail_same_gates(self):
  case=json.loads((P.parent/'pickup-pilot-v31/image-case.json').read_text());r=surface.audit(case,ROOT)
  self.assertFalse(r['numerical_surface_check_pass']);self.assertEqual(r['markers']['surface.far_boot_toe']['range_xy_px'],[55,2]);self.assertEqual(r['markers']['surface.near_boot_toe']['range_xy_px'],[62,5]);self.assertTrue(any(i.get('frame')==5 and i['kind']=='SOURCE_RELATIVE_PHASE_DISAGREEMENT' for i in r['issues']))
 def mutate_receipt(self,mutator):
  # Use a temporary copy of the review directory. Original/raw art is untouched.
  with tempfile.TemporaryDirectory(dir=ROOT/'research/sprite-animation',prefix='review-test-') as temp:
   temp=Path(temp)
   for name in ('parts.json','poses.json','rig-bind-review.json','image-case.json','observer-case.json','visual-review.json'):(temp/name).write_bytes((P/name).read_bytes())
   case=json.loads((P/'review-case.json').read_text());case['directory']=str(temp.relative_to(ROOT));case['evidence_inputs']=[]
   mutator(temp);return review.review(case,ROOT)
 def test_swapped_parent_transforms_block_positive_visual_review(self):
  def mutate(p):
   r=json.loads((p/'rig-bind-review.json').read_text());a,b=[next(row for row in r['frames'][3]['rows'] if row['name']==n) for n in ('right.thigh','left.thigh')];a['matrix'],b['matrix']=b['matrix'],a['matrix'];(p/'rig-bind-review.json').write_text(json.dumps(r))
  r=self.mutate_receipt(mutate);self.assertFalse(r['motion_review_pass']);self.assertTrue(any(not c['pass'] and 'endpoint' in c['name'] for c in r['checks']))
 def test_mirror_blocks_review(self):
  def mutate(p):
   r=json.loads((p/'rig-bind-review.json').read_text());a=next(row for row in r['frames'][3]['rows'] if row['name']=='right.forearm');a['matrix'][0]*=-1;a['matrix'][1]*=-1;(p/'rig-bind-review.json').write_text(json.dumps(r))
  r=self.mutate_receipt(mutate);self.assertFalse(r['motion_review_pass']);self.assertTrue(any(not c['pass'] and 'reflected' in c['name'] for c in r['checks']))
 def test_visual_approval_cannot_transfer_to_new_hash(self):
  def mutate(p):
   v=json.loads((p/'visual-review.json').read_text());v['frames'][3]['sha256']='0'*64;(p/'visual-review.json').write_text(json.dumps(v))
  r=self.mutate_receipt(mutate);self.assertFalse(r['motion_review_pass']);self.assertTrue(any(not c['pass'] and 'visual' in c['name'] for c in r['checks']))
 def test_wrong_clock_blocks_review(self):
  def mutate(p):
   q=json.loads((p/'poses.json').read_text());q[3]['source_time_seconds']+=.04;(p/'poses.json').write_text(json.dumps(q))
  r=self.mutate_receipt(mutate);self.assertFalse(r['motion_review_pass'])
 def test_missing_rig_evidence_cannot_vacuously_pass(self):
  def mutate(p):
   r=json.loads((p/'rig-bind-review.json').read_text());r['frames']=[];(p/'rig-bind-review.json').write_text(json.dumps(r))
  r=self.mutate_receipt(mutate);self.assertFalse(r['motion_review_pass'])
if __name__=='__main__':unittest.main()
