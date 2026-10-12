import importlib.util,json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
loader=importlib.util.spec_from_file_location('sprite_temporal',Path(__file__).parents[1]/'walk-continuity.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[4]
class TemporalModeTests(unittest.TestCase):
 def test_actual_short_repair_preview_plays_once_instead_of_wrapping_to_wrong_phase(self):
  root=ROOT/'research/sprite-animation/leg-ownership-v16/attempt1'
  for ext in ['gif','png','webp']:
   with Image.open(root/('walk-ro-cadence.'+ext)) as im:
    self.assertEqual(im.n_frames,4)
    if ext=='gif':self.assertNotIn('loop',im.info)
    else:self.assertEqual(im.info.get('loop'),1)
 def test_one_shot_excerpt_has_no_artificial_return_jump(self):
  p=[[0,0],[10,0],[20,0]];delta,v,a=m.temporal_differences(p,[100]*3,False);np.testing.assert_array_equal(delta,[[10,0],[10,0]]);np.testing.assert_allclose(a,0);self.assertEqual(len(v),2)
  cyc,_,_=m.temporal_differences(p,[100]*3,True);np.testing.assert_array_equal(cyc[-1],[-20,0])
 def test_actual_bank_excerpt_uses_only_its_three_forward_edges(self):
  p=ROOT/'research/sprite-animation/ground-walk-sixteen-v15/evidence/v15-continuity-observations.json';c=json.loads(p.read_text());c['frames']=c['frames'][8:12];c['loop']=False;c.pop('texture_roi',None);c.pop('palette_patch_probe',None);r=m.audit(c);self.assertEqual(len(r['edges']),3);self.assertFalse(any(e['loop_seam'] for e in r['edges']));self.assertFalse(r['semantic_leg_identity_checked'])
 def test_one_shot_declared_visible_track_does_not_report_a_loop_seam(self):
  p=ROOT/'research/sprite-animation/ground-walk-sixteen-v15/evidence/v15-continuity-observations.json';c=json.loads(p.read_text());c['frames']=c['frames'][:3];c['loop']=False;c.pop('texture_roi',None);c.pop('palette_patch_probe',None);c['tracked_landmarks']=['control_surface']
  for i,f in enumerate(c['frames']):f['landmarks']={'control_surface':{'xy':[100+i*10,100],'uncertainty_px':0}}
  r=m.audit(c);self.assertIsNone(r['landmarks']['control_surface']['last_to_first_step_px']);self.assertEqual(r['landmarks']['control_surface']['max_temporal_second_difference_px'],0);self.assertIsNone(r['landmarks']['control_surface']['max_cyclic_second_difference_px'])
if __name__=='__main__':unittest.main()
