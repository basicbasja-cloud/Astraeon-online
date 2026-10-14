"""Meaningful replacement defects must fail even with an unchanged good motion."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'research/sprite-animation/hair-swap-v33';s=importlib.util.spec_from_file_location('hair_review',ROOT/'skills/modular-eight-direction-sprites/scripts/hair-swap-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class HairReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.case=json.loads((P/'swap-case.json').read_text())
 def test_real_replacements_preserve_body_and_pose(self):
  r=m.review(self.case,ROOT);self.assertTrue(r['replacement_numeric_pass']);self.assertEqual(max(f['changed_pixels_outside_head_pass_union'] for v in r['actual_pixel_measurements'].values() for f in v),0);self.assertFalse(r['full_factory_production_pass'])
 def test_changed_boot_is_caught_outside_head_pass(self):
  a=np.array(Image.open(P/'frames/silver/00.png'));b=a.copy();b[489,198,:3]=[255,0,255];head=np.array(Image.open(P/'head-masks/silver/00.png'));r=m.compare_pixels(a,b,head,head);self.assertEqual(r['changed_pixels_outside_head_pass_union'],1)
 def test_changed_canvas_refused(self):
  a=np.zeros((512,384,4),dtype='uint8')
  with self.assertRaisesRegex(ValueError,'canvas'):m.compare_pixels(a,a[:510],a,a)
 def test_stale_render_refused(self):
  c=copy.deepcopy(self.case);c['styles']['silver'][3]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Stale'):m.review(c,ROOT)
 def temporary_json(self,key,mutator):
  c=copy.deepcopy(self.case);data=json.loads((ROOT/c[key]['path']).read_text());mutator(data)
  with tempfile.TemporaryDirectory(dir=ROOT/'research/sprite-animation',prefix='hair-test-') as temp:
   f=Path(temp)/'changed.json';f.write_text(json.dumps(data));c[key]={'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()};return m.review(c,ROOT)
 def test_one_frame_hair_mount_drift_rejected(self):
  def drift(b):next(r for r in b['silver'][3] if r['name']=='silver.front')['matrix'][4]+=12
  r=self.temporary_json('bindings',drift);self.assertFalse(r['replacement_numeric_pass'])
 def test_depth_order_change_rejected(self):
  def swap(b):b['auburn'][3][13],b['auburn'][3][15]=b['auburn'][3][15],b['auburn'][3][13]
  self.assertFalse(self.temporary_json('bindings',swap)['replacement_numeric_pass'])
 def test_missing_exported_bank_cannot_vacuously_pass(self):
  self.assertFalse(self.temporary_json('bindings',lambda b:b.pop('auburn'))['replacement_numeric_pass'])
 def test_mirrored_hair_rejected(self):
  def reflect(b):next(r for r in b['silver'][3] if r['name']=='silver.front')['matrix'][0]*=-1
  self.assertFalse(self.temporary_json('bindings',reflect)['replacement_numeric_pass'])
 def test_pose_change_cannot_inherit_smoothness_feedback(self):
  def move(q):q[4]['joints']['pelvis'][1]+=7
  self.assertFalse(self.temporary_json('poses',move)['replacement_numeric_pass'])
 def test_color_only_swap_does_not_prove_second_style(self):
  c=copy.deepcopy(self.case);c['head_previews']['auburn']=c['head_previews']['silver'];r=m.review(c,ROOT);self.assertFalse(r['replacement_numeric_pass']);self.assertEqual(r['distinct_silhouette_pixels'],0)
 def test_clock_edit_rejected(self):
  c=copy.deepcopy(self.case);c['styles']['auburn'][4]['duration_ms']+=100;self.assertFalse(m.review(c,ROOT)['replacement_numeric_pass'])
 def test_joined_raw_atlas_preserved_as_failure(self):
  def big(p):
   a=np.array(Image.open(p).convert('RGBA'));n,l,stats,c=cv2.connectedComponentsWithStats((a[:,:,3]>0).astype('uint8'),8);return sorted([r.tolist() for r in stats[1:] if r[4]>5000],key=lambda r:-r[4])
  bad=big(P/'hair-atlas-raw.png');good=big(P/'hair-atlas-repaired-raw.png');self.assertEqual(len(bad),3);self.assertGreater(bad[0][2],1000);self.assertEqual(len(good),4)
if __name__=='__main__':unittest.main()
