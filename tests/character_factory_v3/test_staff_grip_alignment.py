import sys,unittest,math,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from staff_grip_alignment import alignment_angles
from render_staff_grip_study import instrument
class StaffGripTests(unittest.TestCase):
 def test_quarter_pronation_aligns_horizontal_finger_stack(self):
  r=alignment_angles([1,0,0],[0,1,0]);self.assertAlmostEqual(r['forearm_roll_radians'],math.pi/2);self.assertAlmostEqual(r['wrist_flex_radians'],0)
 def test_small_flex_is_separate_from_pronation(self):
  r=alignment_angles([1,0,0],[.2,math.sqrt(.96),0]);self.assertAlmostEqual(r['wrist_flex_radians'],math.asin(.2))
 def test_degenerate_axis_is_rejected(self):
  with self.assertRaises(ValueError):alignment_angles([0,0,1],[1,0,0])
 def test_isolated_adapter_does_not_rewrite_canonical_source(self):
  p=ROOT/'tools/character_factory_v3/render_patch001_guides.py';before=p.read_bytes();tree=instrument(before.decode());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_align_reference_staff_grip'];self.assertEqual(len(calls),1);self.assertEqual(p.read_bytes(),before)
