import json,sys,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from audit_reuse_bindings import audit
class ReuseTests(unittest.TestCase):
 def setUp(self):
  base=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
  self.config=json.loads((base/'factory.json').read_text());self.ledger=json.loads((base/'ledger.json').read_text())
 def test_actual_bindings_pass(self):self.assertTrue(audit(self.config,self.ledger)['passed'])
 def test_old_mage_alias_is_rejected(self):
  self.config['classes']['Mage']['actions']['BasicAttack']['reuse_from']='CastRelease'
  self.assertFalse(audit(self.config,self.ledger)['passed'])
 def test_missing_target_is_rejected(self):
  self.config['classes']['Mage']['actions']['BasicAttack']['reuse_from']='Missing'
  self.assertFalse(audit(self.config,self.ledger)['passed'])
