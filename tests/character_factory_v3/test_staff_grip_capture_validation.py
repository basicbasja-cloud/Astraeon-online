import sys,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from validate_staff_grip_capture import valid_staff_grip_capture
class GripCaptureValidationTests(unittest.TestCase):
 def setUp(self):
  self.job={'staff_grip_alignment_revision':1,'staff_grip_alignment_sha256':'1'*64,'staff_grip_alignment_math_sha256':'2'*64,'renderer_sha256':'3'*64,'staff_arm_reference':'Idle_Lantern','frames':1,'directions':['SW']}
  self.manifest={'staff_grip_adaptation':{'adapter_sha256':'1'*64,'alignment_math_sha256':'2'*64,'canonical_renderer_sha256':'3'*64,'source_glb_modified':False,'reference_adaptations':[{'reference_action':'Idle_Lantern','forearm_roll_degrees':87,'wrist_flex_degrees':19,'aligned_reference_axis_error_degrees':0,'reference_anchor_errors_m':{n:0 for n in ['head','pelvis','foot_r','foot_l','hand_r','hand_l','lowerarm_r']}}],'rendered_grip_checks':[{'image':'SW/000.png','axis_error_degrees':0,'grip_axis_distance_m':0}]}}
 def test_complete_capture(self):self.assertTrue(valid_staff_grip_capture(self.job,self.manifest))
 def test_missing_grip_evidence_is_not_cache_hit(self):self.assertFalse(valid_staff_grip_capture(self.job,{}))
 def test_rotated_or_detached_staff_is_rejected(self):
  for key,value in [('axis_error_degrees',90),('grip_axis_distance_m',.02)]:
   m=copy.deepcopy(self.manifest);m['staff_grip_adaptation']['rendered_grip_checks'][0][key]=value;self.assertFalse(valid_staff_grip_capture(self.job,m))
 def test_body_anchor_change_is_rejected(self):
  self.manifest['staff_grip_adaptation']['reference_adaptations'][0]['reference_anchor_errors_m']['foot_r']=.01;self.assertFalse(valid_staff_grip_capture(self.job,self.manifest))
 def test_boolean_rotation_cannot_masquerade_as_number(self):
  self.manifest['staff_grip_adaptation']['reference_adaptations'][0]['forearm_roll_degrees']=True;self.assertFalse(valid_staff_grip_capture(self.job,self.manifest))
 def test_stale_math_proof_is_rejected(self):
  self.manifest['staff_grip_adaptation']['alignment_math_sha256']='0'*64;self.assertFalse(valid_staff_grip_capture(self.job,self.manifest))
 def test_missing_view_is_rejected(self):
  self.job['directions'].append('NE');self.assertFalse(valid_staff_grip_capture(self.job,self.manifest))
