import importlib.util,json,copy,hashlib,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];D=ROOT/'research/sprite-animation/weighted-slash-v27';S=ROOT/'skills/modular-eight-direction-sprites/scripts/attack-weight-review.py';spec=importlib.util.spec_from_file_location('weight',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class WeightReview(unittest.TestCase):
 def test_actual_weak_source_retains_three_failure_classes(self):
  case=json.loads((D/'evidence/v26-weight-case.json').read_text());r=m.audit(case,ROOT)
  self.assertIn('source_transfer_below_declared_family_target',r['issues']);self.assertIn('source_trunk_acting_below_declared_family_target',r['issues']);self.assertIn('source_stops_or_slows_at_intermediate_cut_key',r['issues'])
 def test_reauthored_source_improves_but_does_not_approve_art(self):
  r=m.audit(json.loads((D/'evidence/v27-weight-case.json').read_text()),ROOT)
  self.assertGreater(r['measurements']['source_mid_cut_speed_ratio'],.9);self.assertIn('painted_weight_and_wrist_observations_unknown',r['issues']);self.assertFalse(r['production_pass'])
 def test_changed_source_binding_rejected(self):
  c=json.loads((D/'evidence/v27-weight-case.json').read_text());c['source_index']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Changed evidence'):m.audit(c,ROOT)
 def test_correct_source_cannot_hide_unknown_painted_joints(self):
  c=json.loads((D/'evidence/v27-weight-case.json').read_text());p=D/'rig-source/SE/00.png';c['art']={'acting_accepted_by_user':False,'frames':[{'key':0,'path':str(p.relative_to(ROOT)),'sha256':m.sha(p),'points':{'pelvis':None,'shoulder':None},'anatomical_right_chain_verified':False}]};r=m.audit(c,ROOT)
  self.assertIn('painted_pelvis_unknown',r['issues']);self.assertIn('painted_right_chain_identity_unverified',r['issues']);self.assertFalse(r['production_pass'])
if __name__=='__main__':unittest.main()
