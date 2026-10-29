import sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import audit_swordsman_walk_sole_donor as audit
class WalkSoleDonorTests(unittest.TestCase):
 def test_brown_search_and_empty_guard(self):
  im=Image.new('RGB',(40,40),'white')
  with self.assertRaises(ValueError):audit.nearest_brown(im,(20,20))
  im.putpixel((20,21),(120,70,40));point,d=audit.nearest_brown(im,(20,20));self.assertEqual(point,[20,21]);self.assertEqual(d,1.)
 def test_refuses_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):audit.build(Path(d))
if __name__=='__main__':unittest.main()
