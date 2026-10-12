import importlib.util,json,math,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
maths=module('compactmath',ROOT/'skills/modular-eight-direction-sprites/studies/walk-test/compact_gait_math.py')
checker=module('compactcheck',ROOT/'skills/modular-eight-direction-sprites/scripts/compact-gait-check.py')
class CompactGaitTests(unittest.TestCase):
 def test_path_position_and_velocity_continuity_at_release_and_wrap(self):
  eps=1e-6
  for p in [.6,1]:
   a=maths.foot_path(p-eps);b=maths.foot_path(p);c=maths.foot_path(p+eps)
   for j in [0,1]:self.assertAlmostEqual((b[j]-a[j])/eps,(c[j]-b[j])/eps,places=4)
 def test_stance_root_cancellation_and_small_swing(self):
  values=[maths.foot_path(i/1000) for i in range(1000)]
  self.assertAlmostEqual(max(v[1] for v in values),.04)
  for p in [0,.1,.3,.599]:self.assertAlmostEqual(maths.foot_path(p)[0]-.42*p,-.14)
 def test_no_both_swing_for_default_stance(self):
  for i in range(1000):self.assertTrue(maths.foot_path(i/1000)[1]==0 or maths.foot_path(i/1000+.5)[1]==0)
 def test_roll_continuity_and_flat_stance(self):
  for p in [.07,.5,.6,1]:self.assertAlmostEqual(maths.roll(p-1e-6),maths.roll(p+1e-6),places=5)
  for p in [.1,.25,.49]:self.assertEqual(maths.roll(p),0)
 def test_invalid_authoring_parameters_fail(self):
  for kwargs in [{'stance':1},{'stance':0},{'stride':-1},{'lift':-1},{'phase':float('nan')}]:
   params={'phase':0};params.update(kwargs)
   with self.assertRaises(ValueError):maths.foot_path(**params)
 def test_saved_actual_dense_source_passes_only_source_scope(self):
  r=checker.inspect(ROOT/'research/sprite-animation/ro-gait-v17/evidence/source-contract.json');self.assertTrue(r['source_checks_passed']);self.assertEqual(r['dense_samples'],257);self.assertFalse(r['production_ready']);self.assertFalse(r['painted_anatomy_verified'])
 def test_stale_binding_and_tighter_posture_budget_fail(self):
  c=json.loads((ROOT/'research/sprite-animation/ro-gait-v17/evidence/source-contract.json').read_text())
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'contract.json';bad=dict(c);bad['ground_sha256']='0'*64;p.write_text(json.dumps(bad))
   with self.assertRaises(ValueError):checker.inspect(p)
   c['budgets']['sagittal_tilt_deg']=1;p.write_text(json.dumps(c));r=checker.inspect(p);self.assertFalse(r['source_checks_passed']);self.assertIn('source posture',r['failed_source_checks'])
 def test_actual_dense_between_key_drift_is_not_hidden_by_bake_checks(self):
  c=json.loads((ROOT/'research/sprite-animation/ro-gait-v17/evidence/source-contract.json').read_text());g=json.loads((ROOT/c['ground_path']).read_text())
  # Mutate only one between-key evaluated vertex sample, with a valid new hash.
  g['dense_samples'][51]['soles']['sole.left.heel']['fixed_sole_vertex_world_traveled'][0]+=.001
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'ground.json';p.write_text(json.dumps(g));c['ground_path']=str(p);c['ground_sha256']=checker.sha(p);contract=Path(d)/'contract.json';contract.write_text(json.dumps(c));r=checker.inspect(contract);self.assertIn('flat-support vertex drift',r['failed_source_checks']);self.assertFalse(r['source_checks_passed'])
if __name__=='__main__':unittest.main()
