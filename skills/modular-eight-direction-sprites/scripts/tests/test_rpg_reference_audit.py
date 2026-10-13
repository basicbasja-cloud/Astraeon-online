import copy,gzip,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
path=ROOT/'skills/modular-eight-direction-sprites/scripts/rpg-reference-audit.py'
spec=importlib.util.spec_from_file_location('rpg',path);rpg=importlib.util.module_from_spec(spec);spec.loader.exec_module(rpg)
STUDY=ROOT/'research/sprite-animation/rpg-motion-foundation-v29'
class RPGReferenceTests(unittest.TestCase):
 def setUp(self):
  self.catalog=json.loads((STUDY/'sources.json').read_text());self.taxonomy=json.loads((STUDY/'motions.json').read_text())
 def test_actual_research_specs_have_no_dangling_or_unapproved_scope(self):self.assertEqual(rpg.specs(self.catalog,self.taxonomy),[])
 def test_dash_research_is_not_implicitly_committed_gameplay(self):
  dash=next(m for m in self.taxonomy['motions'] if m['id']=='dash.forward');dash['gameplay_committed']=True;self.assertIn('dash_not_optional:dash.forward',rpg.specs(self.catalog,self.taxonomy))
 def test_old_attack_reintroduced_is_rejected(self):
  self.catalog['sources'][0]['old_own_attack_reference']=True;self.assertIn('old_attack_source:ro-act',rpg.specs(self.catalog,self.taxonomy))
 def test_unknown_motion_cannot_be_promoted_to_production(self):
  self.taxonomy['motions'][0]['production_approved']=True;self.assertIn('unearned_production_approval:idle.relaxed',rpg.specs(self.catalog,self.taxonomy))
 def test_source_typo_is_not_coverage(self):
  self.taxonomy['motions'][0]['reference_leads']=['missing'];self.assertIn('dangling_source:idle.relaxed',rpg.specs(self.catalog,self.taxonomy))
 def test_actual_capture_clock_and_native_holds(self):
  c=json.loads((STUDY/'captures/kaykit-preview-1/capture.json').read_text());self.assertEqual(rpg.capture_errors(c),[]);self.assertEqual(len(c['frames']),250)
 def test_reordering_or_omitting_frame_is_rejected(self):
  c=json.loads((STUDY/'captures/kaykit-preview-1/capture.json').read_text());c['frames'][1],c['frames'][2]=c['frames'][2],c['frames'][1]
  self.assertIn('ordinal_order',rpg.capture_errors(c));self.assertIn('native_clock_discontinuity',rpg.capture_errors(c))
 def test_resampling_time_without_new_receipt_is_rejected(self):
  c=json.loads((STUDY/'captures/kaykit-preview-1/capture.json').read_text());c['frames'][1]['source_pts_ms']+=10;self.assertIn('native_clock_discontinuity',rpg.capture_errors(c))
 def test_path_escape_is_not_a_corpus_asset(self):
  with self.assertRaises(ValueError):rpg.safe(STUDY,'../outside.png')
 def test_actual_joint_head_and_parent_local_matrices_are_independently_consistent(self):
  f=json.loads(gzip.decompress((STUDY/'preset-samples.json.gz').read_bytes()))['files'][0];s=f['clips'][0]['samples'][0];self.assertLess(rpg.matrix_residual(s,f['bones']),2e-5)
  n=next(iter(s['world_joints']));s['world_joints'][n][0]+=1;self.assertGreater(rpg.matrix_residual(s,f['bones']),.9)
 def test_nonfinite_matrix_cannot_pass_integrity(self):
  f=json.loads(gzip.decompress((STUDY/'preset-samples.json.gz').read_bytes()))['files'][0];s=f['clips'][0]['samples'][0];n=next(iter(s['world_joints']));s['world_bone_matrices'][n][0][0]=float('nan')
  with self.assertRaises(ValueError):rpg.matrix_residual(s,f['bones'])
 def test_actual_full_corpus_never_implies_art_accuracy_or_production(self):
  result=rpg.audit(STUDY);self.assertTrue(result['corpus_integrity_pass']);self.assertFalse(result['production_pass']);self.assertIsNone(result['art_anatomy_accuracy']);self.assertEqual(result['counts']['motion_candidates'],71);self.assertEqual(result['counts']['dash_included'],6)
if __name__=='__main__':unittest.main()
