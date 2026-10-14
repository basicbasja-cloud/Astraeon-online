import copy,importlib.util,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'research/sprite-animation/pickup-view-v34';S=Path(__file__).parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v2=load('observerv2',S/'rigid-surface-observer-v2.py');v1=load('observerv1',S/'rigged-surface-observer.py')
class SurfaceObserverV2(unittest.TestCase):
 def setUp(self):self.case=json.loads((P/'original-observer-case.json').read_text())
 def test_actual_v2_all24_surfaces_under_same_thresholds(self):
  r=v2.observe(self.case,ROOT);self.assertTrue(all(o['status']=='visible' for t in r['tracks'].values() for o in t));self.assertFalse(r['later_pose_coordinates_used']);self.assertEqual(self.case['patches']['surface.reaching_cuff']['minimum_ncc'],.95)
 def test_unchanged_v1_retains_actual_abstentions(self):
  r=v1.observe(self.case,ROOT);self.assertEqual([o['frame'] for o in r['tracks']['surface.reaching_cuff'] if o['status']=='unknown'],[1,2])
 def test_changed_image_hash_refused(self):
  self.case['frames'][2]['sha256']='0'*64
  with self.assertRaises(ValueError):v2.observe(self.case,ROOT)
 def test_erased_surface_stays_unknown(self):
  frames=[v2.read_bound(ROOT,r) for r in self.case['frames']];frames[3]=np.zeros_like(frames[3]);s=self.case['patches']['surface.reaching_cuff'];isolated=v2.read_bound(ROOT,s['isolated_first_frame']);self.assertEqual(v2.match(frames,s,isolated)[3]['status'],'unknown')
 def test_blank_calibration_cannot_claim_match(self):
  with self.assertRaises(ValueError):v2.match([np.zeros((512,384,4),dtype='uint8')],self.case['patches']['surface.near_boot_toe'])
if __name__=='__main__':unittest.main()
