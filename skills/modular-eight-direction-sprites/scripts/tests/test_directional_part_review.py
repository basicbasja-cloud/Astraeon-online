"""Actual bound new-view controls, including retained generated hair failure."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'research/sprite-animation/pickup-view-v34'
s=importlib.util.spec_from_file_location('directional',Path(__file__).parents[1]/'directional-part-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
class DirectionalPartReview(unittest.TestCase):
 def setUp(self):self.case=json.loads((P/'view-case.json').read_text());self.tmp=tempfile.TemporaryDirectory(dir=ROOT);self.addCleanup(self.tmp.cleanup)
 def changed(self,key,edit):
  data=json.loads((ROOT/self.case[key]['path']).read_text());edit(data);p=Path(self.tmp.name)/(key+'.json');p.write_text(json.dumps(data));self.case[key]=bind(p)
 def test_real_new_view(self):self.assertTrue(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_changed_frame_hash_fails(self):
  self.case['styles']['silver'][3]['sha256']='0'*64
  with self.assertRaises(ValueError):m.review(self.case,ROOT)
 def test_wrong_view_row_fails(self):
  self.changed('bindings',lambda b:b['silver'][3][0].update(view='A'));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_mirrored_part_matrix_fails(self):
  self.changed('bindings',lambda b:b['silver'][3][0]['matrix'].__setitem__(0,-b['silver'][3][0]['matrix'][0]));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_swapped_joint_side_fails(self):
  self.changed('bindings',lambda b:next(r for r in b['original'][3] if r['name']=='right.forearm').update(joint_chain=['left.elbow','left.wrist']));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_one_frame_foot_jump_fails(self):
  self.changed('bindings',lambda b:next(r for r in b['silver'][3] if r['name']=='right.foot')['matrix'].__setitem__(4,40));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_same_camera_is_not_new_view(self):
  old=json.loads((ROOT/self.case['original_source']['path']).read_text());self.changed('source',lambda d:d.update(camera_world_matrix=old['camera_world_matrix']));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_retained_real_hair_failure_rejected(self):
  self.case['styles']['silver'][3].update(bind(P/'failure-controls/hair-misfit.png'));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_numerical_pass_never_grants_production(self):self.assertFalse(m.review(self.case,ROOT)['production_pass'])
 def test_all_styles_same_foot_jump_still_fails_mount(self):
  def edit(b):
   for s in b:next(r for r in b[s][3] if r['name']=='right.foot')['matrix'][4]+=20
  self.changed('bindings',edit);self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_one_wrong_knee_overlap_order_fails(self):
  def edit(b):
   rows=b['silver'][3];a=next(i for i,r in enumerate(rows) if r['name']=='left.shin');z=next(i for i,r in enumerate(rows) if r['name']=='left.thigh');rows[a],rows[z]=rows[z],rows[a]
  self.changed('bindings',edit);self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
 def test_changed_pose_clock_fails(self):
  self.changed('poses',lambda p:p[3].update(source_time_seconds=.7));self.assertFalse(m.review(self.case,ROOT)['numeric_view_check_pass'])
if __name__=='__main__':unittest.main()
