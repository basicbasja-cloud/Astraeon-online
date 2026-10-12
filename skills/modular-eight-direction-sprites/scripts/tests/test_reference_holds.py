import copy,importlib.util,json,unittest
from pathlib import Path
SCRIPT=Path(__file__).parents[1];ROOT=SCRIPT.parents[2]
spec=importlib.util.spec_from_file_location('holds',SCRIPT/'reference-holds.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class HoldTests(unittest.TestCase):
 def setUp(self):self.case=json.loads((ROOT/'research/sprite-animation/ro-attack-paintover-v22/evidence/attempt3-body-hold-case.json').read_text())
 def test_real_captured_holds(self):
  r=m.audit(self.case,ROOT);self.assertEqual(r['unique_body_keys'],6);self.assertEqual(r['duration_ms'],900);self.assertEqual(r['body_sha256_per_exposure'][2],r['body_sha256_per_exposure'][3]);self.assertFalse(r['production_ready'])
 def test_wrong_phase_rejected(self):
  self.case['exposure_to_body_key'][3]=1
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_changed_master_rejected(self):
  self.case['body_keys'][0]['sha256']='0'*64
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_missing_exposure_rejected(self):
  self.case['exposure_to_body_key'].pop()
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_fake_source_bones_rejected(self):
  self.case['recovered_hidden_skeleton']=True
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_fake_world_contact_rejected(self):
  self.case['world_contacts_verified']=True
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_missing_body_key_rejected(self):
  self.case['body_keys'].pop()
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
 def test_changed_canvas_rejected(self):
  self.case['canvas']=[256,256]
  with self.assertRaises(ValueError):m.audit(self.case,ROOT)
if __name__=='__main__':unittest.main()
