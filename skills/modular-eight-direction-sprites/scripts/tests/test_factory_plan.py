import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('factoryplan',ROOT/'skills/modular-eight-direction-sprites/scripts/factory-plan.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class FactoryPlanTests(unittest.TestCase):
 def setUp(self):self.path=ROOT/'research/sprite-animation/cross-game-factory-v18/evidence/factory-contract.json';self.c=json.loads(self.path.read_text())
 def compile(self,c):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'contract.json';p.write_text(json.dumps(c));return m.compile_plan(p)
 def test_actual_approved_motion_yields_exact_pose_and_item_jobs(self):
  r=m.compile_plan(self.path);self.assertEqual(len(r['poses']),16);self.assertEqual(r['planned_part_frame_jobs'],208);self.assertEqual(r['duration_ms'],800);self.assertEqual(r['completed_painted_jobs'],0);self.assertFalse(r['production_ready'])
 def test_authoritative_export_camera_not_inherited_saved_metadata(self):
  r=m.compile_plan(self.path);self.assertEqual(r['canvas'],[512,512]);self.assertTrue(all(p['playback_duration_ms']==50 for p in r['poses']))
 def test_hair_items_are_alternatives_of_one_logical_slot(self):
  r=m.compile_plan(self.path);self.assertEqual(r['source_item_groups_count'],13);self.assertEqual(r['logical_slot_count'],12);hair=[j for j in r['part_frame_jobs'] if j['logical_slot']=='hair'];self.assertEqual(len(hair),32);self.assertEqual({j['variant'] for j in hair},{'silver','auburn'})
 def test_stale_approval_fails(self):
  self.c['approval']['sha256']='0'*64
  with self.assertRaises(ValueError):self.compile(self.c)
 def test_unapproved_facing_fails(self):
  self.c['facing']='E'
  with self.assertRaisesRegex(ValueError,'Unapproved facing'):self.compile(self.c)
 def test_inventory_from_other_approval_fails_even_with_new_valid_file_hash(self):
  d=json.loads((ROOT/self.c['inventory']['path']).read_text());d['approval_sha256']='0'*64
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/'inventory.json';f.write_text(json.dumps(d));self.c['inventory']={'path':str(f),'sha256':m.sha(f)}
   with self.assertRaisesRegex(ValueError,'another approved source'):self.compile(self.c)
if __name__=='__main__':unittest.main()
