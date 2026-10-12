import importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];s=importlib.util.spec_from_file_location('atlasreference',ROOT/'skills/modular-eight-direction-sprites/scripts/reference-atlas.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReferenceAtlasTests(unittest.TestCase):
 def setUp(self):self.root=ROOT/'research/sprite-animation/cross-game-factory-v18';self.walk=json.loads((self.root/'evidence/valyria-walk-west-contract.json').read_text());self.attack=json.loads((self.root/'evidence/valyria-attack-contract.json').read_text())
 def run_case(self,c):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps(c));return m.extract(p,Path(d)/'output')
 def test_repeat_atlas_ids_keep_distinct_exposures_and_same_pixels(self):
  r=self.run_case(self.walk);self.assertEqual(len(r['frames']),6);self.assertEqual(r['frames'][0]['source_atlas_id'],r['frames'][3]['source_atlas_id']);self.assertEqual(r['frames'][0]['sha256'],r['frames'][3]['sha256']);self.assertEqual(r['duration_ms'],780)
 def test_terminal_hold_stays_unknown_duration_and_never_becomes_a_loop(self):
  r=self.run_case(self.attack);self.assertIsNone(r['duration_ms']);self.assertEqual(r['finite_duration_ms'],580);self.assertIsNone(r['frames'][-1]['duration_ms']);self.assertFalse(r['loop']);self.assertEqual(r['canvas'],[64,64])
 def test_changed_atlas_fails(self):
  self.walk['image_sha256']='0'*64
  with self.assertRaises(ValueError):self.run_case(self.walk)
 def test_bad_id_fails(self):
  self.walk['exposures'][0]['id']=24
  with self.assertRaises(ValueError):self.run_case(self.walk)
 def test_unknown_duration_cannot_be_inserted_mid_clip(self):
  self.attack['exposures'][0]={'id':0,'duration_ms':None,'hold':'until_state_change'}
  with self.assertRaises(ValueError):self.run_case(self.attack)
 def test_terminal_hold_not_allowed_in_loop(self):
  self.attack['loop']=True
  with self.assertRaises(ValueError):self.run_case(self.attack)
if __name__=='__main__':unittest.main()
