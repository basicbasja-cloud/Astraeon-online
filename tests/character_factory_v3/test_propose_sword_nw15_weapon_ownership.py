import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from propose_sword_nw15_weapon_ownership import build, BASE, ORDER

class SwordOwnershipProposalTests(unittest.TestCase):
 def test_same_frame_recomposition_and_unchanged_head_fx(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'candidate';report=build(out)
   self.assertTrue(report['master_rgba_exact']);self.assertFalse(report['art_approved']);self.assertFalse(report['runtime_admitted'])
   self.assertGreater(report['transferred_pixels_by_prior_role']['BodyCostume'],0)
   self.assertGreater(report['transferred_pixels_by_prior_role']['WeaponHandOccluder'],0)
   old=BASE/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack/NW'
   for role in ['HeadHair','WeaponLightBack','WeaponLightFront']:
    self.assertEqual(Image.open(out/'layers'/f'{role}.png').convert('RGBA').tobytes(),Image.open(old/role/'015.png').convert('RGBA').tobytes())
   composite=Image.new('RGBA',(768,768))
   for role in ORDER:composite.alpha_composite(Image.open(out/'layers'/f'{role}.png').convert('RGBA'))
   self.assertEqual(composite.tobytes(),Image.open(out/'master.png').convert('RGBA').tobytes())

 def test_existing_output_is_never_overwritten(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'fresh'):build(Path(tmp))

if __name__=='__main__':unittest.main()
