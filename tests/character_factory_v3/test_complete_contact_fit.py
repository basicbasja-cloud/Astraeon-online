import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from fit_complete_master_contacts import fit_contacts
class ContactFitTests(unittest.TestCase):
 def test_one_scale_and_whole_frame_translation(self):
  a=np.array([[[10,20],[30,22]],[[16,30],[36,32]]]);b=a*.8+np.array([[[4,5]],[[6,8]]]);s,t,r=fit_contacts(a,b)
  self.assertAlmostEqual(s,.8);self.assertLess(r.max(),1e-10)
 def test_nonrigid_boot_span_remains_visible(self):
  a=[[[0,0],[20,0]],[[0,0],[40,0]]];b=[[[0,0],[20,0]],[[0,0],[20,0]]]
  self.assertGreater(fit_contacts(a,b)[2].max(),1)
 def test_coincident_feet_fail(self):
  with self.assertRaises(ValueError):fit_contacts([[[0,0],[0,0]]],[[[0,0],[0,0]]])
