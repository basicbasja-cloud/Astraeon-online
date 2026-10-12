"""Actual approved/rejected fixture plus bounded appearance/registration controls.

Requires optional OpenCV. These are structure-comparison checks, not semantic
anatomy benchmark accuracy. All altered test pixels stay in temporary fixtures.
"""
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
try:import cv2
except ImportError:cv2=None
if cv2:
    sys.path.insert(0,str(HERE));s=importlib.util.spec_from_file_location('profile_structure',HERE/'profile-structure.py');module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
@unittest.skipUnless(cv2,'OpenCV is optional; run with the documented vision dependency path')
class ProfileStructureTests(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/'research/sprite-animation/profile-depth-v12';self.spec=json.loads((self.root/'evidence/W-pose-3-structure-reference.json').read_text());self.reference=self.root/'master/W/frames/02.png';self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    def test_approved_actual_reference_matches_without_anatomy_claim(self):
        r,*_=module.compare(self.reference,self.reference,self.spec);self.assertEqual(r['status'],'REFERENCE_STRUCTURE_MATCH_WITHIN_BUDGET');self.assertFalse(r['anatomy_pass']);self.assertFalse(r['semantic_leg_swap_detected'])
    def test_actual_user_rejected_third_pose_has_independent_structural_flag(self):
        r,*_=module.compare(self.reference,self.root/'evidence/user-rejected-new-W-pose-3-diagnostic.png',self.spec);self.assertEqual(r['status'],'STRUCTURAL_DIFFERENCE_REQUIRES_REVIEW');self.assertTrue(any(x['symmetric_p95_distance_px']>8 for x in r['regions']));self.assertFalse(r['semantic_leg_swap_detected'])
    def test_small_shared_registration_shift_is_not_a_leg_error(self):
        a=np.array(Image.open(self.reference).convert('RGBA'));b=cv2.warpAffine(a,np.float32([[1,0,6],[0,1,-5]]),(512,512));p=Path(self.tmp.name)/'translation.png';Image.fromarray(b).save(p)
        r,*_=module.compare(self.reference,p,self.spec);self.assertEqual(r['status'],'REFERENCE_STRUCTURE_MATCH_WITHIN_BUDGET');self.assertFalse(r['registration']['leg_fit_used'])
    def test_small_lighting_change_is_not_a_leg_error(self):
        a=np.array(Image.open(self.reference).convert('RGBA'));a[:,:,:3]=np.rint(a[:,:,:3]*.94).astype(np.uint8);p=Path(self.tmp.name)/'brightness.png';Image.fromarray(a).save(p)
        r,*_=module.compare(self.reference,p,self.spec);self.assertEqual(r['status'],'REFERENCE_STRUCTURE_MATCH_WITHIN_BUDGET')
    def test_no_texture_or_usable_registration_returns_inconclusive(self):
        p=Path(self.tmp.name)/'empty.png';Image.new('RGBA',(512,512)).save(p);r,*_=module.compare(self.reference,p,self.spec);self.assertEqual(r['status'],'INCONCLUSIVE');self.assertFalse(r['anatomy_pass'])
    def test_different_canvas_is_not_silently_fitted(self):
        p=Path(self.tmp.name)/'size.png';Image.new('RGBA',(256,256)).save(p)
        with self.assertRaisesRegex(ValueError,'canvases differ'):module.compare(self.reference,p,self.spec)
if __name__=='__main__':unittest.main()
