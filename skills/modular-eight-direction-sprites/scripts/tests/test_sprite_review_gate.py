import copy,importlib.util,json,unittest
from pathlib import Path
loader=importlib.util.spec_from_file_location('review_gate',Path(__file__).parents[1]/'sprite-review-gate.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[4]
class ReviewGateTests(unittest.TestCase):
 def setUp(self):
  self.root=ROOT/'research/sprite-animation';self.source=self.root/'ground-walk-sixteen-v15/source/source-ground.json';self.rejection=self.root/'leg-ownership-v16/evidence/user-rejected-v15-sequence.json';self.old=self.root/'ground-walk-sixteen-v15/candidate/frames'
 def case(self):return m.initialize([self.old/f'{k:02}.png' for k in [8,9,10]],self.source,[8,9,10],[self.rejection])
 def test_real_rejected_sequence_blocks_even_when_floor_or_manual_fields_claim_success(self):
  c=self.case()
  for f in c['frames']:f['anatomy_review']={k:'confirmed' for k in f['anatomy_review']};f['floor_score']='PASS'
  r=m.audit(c);self.assertEqual(r['status'],'REJECTED');self.assertTrue(all(f['status']=='REJECTED_SEQUENCE_MEMBER' for f in r['frames']));self.assertFalse(r['semantic_classifier_used']);self.assertFalse(r['production_ready'])
 def test_relabeling_source_phase_does_not_clear_same_rejected_pixels(self):
  c=self.case();c['frames'][0]['source_key']=9;c['frames'][0]['source_sample_position']=22.5;self.assertEqual(m.audit(c)['frames'][0]['status'],'REJECTED_SEQUENCE_MEMBER')
 def test_fractional_source_time_is_preserved(self):
  c=self.case();self.assertEqual(m.audit(c)['frames'][1]['source_sample_position'],22.5)
  c['frames'][1]['source_sample_position']=22
  with self.assertRaisesRegex(ValueError,'truncated'):m.audit(c)
 def test_other_pixels_do_not_inherit_old_rejection_or_anatomical_approval(self):
  c=m.initialize([self.old/'00.png'],self.source,[0],[self.rejection]);r=m.audit(c);self.assertEqual(r['frames'][0]['status'],'ANATOMY_REVIEW_REQUIRED');self.assertFalse(r['complete_anatomy_accepted'])
 def test_stale_rejection_or_candidate_binding_is_rejected(self):
  c=self.case();c['rejection_receipts'][0]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'rejection'):m.audit(c)
  c=self.case();c['frames'][0]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'candidate'):m.audit(c)
 def test_source_side_and_facing_cannot_be_changed_to_suit_drawing(self):
  c=self.case();r=m.audit(c);self.assertTrue(all(f['source_near_side']=='left' for f in r['frames']));c['facing']='E'
  with self.assertRaisesRegex(ValueError,'Facing'):m.audit(c)
if __name__=='__main__':unittest.main()
