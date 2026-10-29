import sys,unittest
from pathlib import Path
from types import SimpleNamespace as N
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_hit_frozen_feet as audit
class HitFeetAuditTests(unittest.TestCase):
 def test_weight_threshold_and_group_selection(self):
  groups={'foot_l':N(index=3),'ball_l':N(index=4)}
  vertices=[N(index=0,groups=[N(group=3,weight=.6)]),N(index=1,groups=[N(group=4,weight=.4)]),N(index=2,groups=[N(group=8,weight=.9)]),N(index=3,groups=[N(group=4,weight=.5)])]
  mesh=N(vertex_groups=groups,data=N(vertices=vertices))
  self.assertEqual(audit.indices_by_weight(mesh,'l'),[0,3])
 def test_missing_group_raises(self):
  with self.assertRaises(ValueError):audit.indices_by_weight(N(vertex_groups={},data=N(vertices=[])),'r')
if __name__=='__main__':unittest.main()
