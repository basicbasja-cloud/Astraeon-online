import json,sys,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from build_action_inventory import build_inventory
class InventoryTests(unittest.TestCase):
 def setUp(self):
  self.base=ROOT/'authoring/characters/factory-v3/patch-0.0.1';self.config=json.loads((self.base/'factory.json').read_text());self.ledger=json.loads((self.base/'ledger.json').read_text())
 def test_all_six_characters_and_logical_actions(self):
  r=build_inventory(self.config,self.ledger,self.base);self.assertEqual(r['logical_actions'],114);self.assertEqual(r['unique_paint_jobs'],96);self.assertEqual(len({x['character'] for x in r['rows']}),6);self.assertEqual(r['completed_characters'],0);self.assertFalse(any(x['gameplay_approved'] for x in r['rows']))
 def test_mage_24_and_16_frame_jobs_stay_distinct(self):
  r=build_inventory(self.config,self.ledger,self.base);rows={x['action']:x for x in r['rows'] if x['character']=='mage-male-patch001'}
  self.assertEqual(rows['BasicAttack']['frames'],24);self.assertEqual(rows['CastRelease']['frames'],16);self.assertNotEqual(rows['BasicAttack']['paint_job'],rows['CastRelease']['paint_job'])
 def test_missing_paint_binding_is_not_silently_counted(self):
  self.ledger['paint_jobs']={}
  with self.assertRaisesRegex(ValueError,'exactly one'):build_inventory(self.config,self.ledger,self.base)
