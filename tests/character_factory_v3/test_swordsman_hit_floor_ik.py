import sys,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import hit_transition_floor_ik as ik
import render_swordsman_hit_floor_ik_study as render
class HitFloorIKTest(unittest.TestCase):
 def test_no_adjustment_outside_transition_and_at_idle_endpoint(self):
  modules={'bpy':types.ModuleType('bpy'),'mathutils':types.SimpleNamespace(Matrix=object,Vector=object)}
  with patch.dict(sys.modules,modules):
   self.assertEqual(ik.apply(None,{}),{'applied':False,'reason':'not transition'})
   self.assertEqual(ik.apply(None,{'transition_weight':1.}),{'applied':False,'reason':'preserve exact target idle pose'})
 def test_renderer_hook_marker_is_unique(self):
  source=render.base.patched_source(render.base.BASE.read_text())
  self.assertEqual(source.count(render.MARK),1)
if __name__=='__main__':unittest.main()
