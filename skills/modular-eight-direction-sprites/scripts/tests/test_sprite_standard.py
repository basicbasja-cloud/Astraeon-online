import importlib.util,json,tempfile,unittest
from pathlib import Path
loader=importlib.util.spec_from_file_location('sprite_standard',Path(__file__).parents[1]/'sprite-standard.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[4]
class SpriteStandardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=ROOT/'research/sprite-animation/leg-ownership-v16';cls.old=json.loads((cls.root/'evidence/old-standard-contract.json').read_text());cls.new=json.loads((cls.root/'evidence/new-standard-contract.json').read_text());cls.old_report=m.audit(cls.old);cls.new_report=m.audit(cls.new)
 def test_real_rejected_images_cannot_pass_combined_gate_through_surface_or_floor_scores(self):
  self.assertEqual(self.old_report['status'],'REJECTED');self.assertIn('confirmed_rejected_image_sequence',self.old_report['blockers']);self.assertFalse(self.old_report['production_ready'])
 def test_new_drawings_with_unknown_ownership_and_contacts_are_not_accepted(self):
  self.assertEqual(self.new_report['status'],'REVIEW_REQUIRED');self.assertIn('anatomy_acceptance_unresolved',self.new_report['blockers']);self.assertIn('unknown_visible_contact_samples',self.new_report['blockers']);self.assertFalse(self.new_report['production_ready'])
 def test_mixing_stages_from_different_actual_frame_banks_is_rejected(self):
  c=dict(self.new);c['continuity']=self.old['continuity']
  with self.assertRaisesRegex(ValueError,'same frame bank'):m.audit(c)
 def test_loop_and_one_shot_contract_cannot_be_silently_swapped(self):
  c=dict(self.new);c['loop']=False
  with self.assertRaisesRegex(ValueError,'Loop contract'):m.audit(c)
if __name__=='__main__':unittest.main()
