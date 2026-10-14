import copy,importlib.util,json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];V=P.parent/'coherent-motion-v38'
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
tool=module('isolated','skills/modular-eight-direction-sprites/scripts/isolated-key-review.py')
neck=module('neck','skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py')
alpha=module('alpha','skills/modular-eight-direction-sprites/scripts/coherent-strip-alpha.py')
before=json.loads((V/'motion-contract.json').read_text());after=json.loads((P/'motion-contract.json').read_text());normalization=json.loads((P/'normalization.json').read_text())
def run(case=after,norm=normalization):return tool.audit(before,case,V/'renders/review',P/'renders/review',norm,ROOT)

class Controls(unittest.TestCase):
    def test_actual_single_key_preserves_other_seven(self):
        r=run();self.assertTrue(r['isolation_pass']);self.assertTrue(r['other_seven_unchanged']);self.assertGreater(r['target_body_opaque_changed_pixels'],100)
    def test_changed_nontarget_attachment_is_rejected(self):
        case=copy.deepcopy(after);case['variants']['review'][3]['head_matrix'][4]+=1
        self.assertFalse(run(case)['isolation_pass'])
    def test_changed_clock_is_rejected(self):
        case=copy.deepcopy(after);case['clocks']['game'][0]=80
        self.assertFalse(run(case)['isolation_pass'])
    def test_relaxed_contact_budget_is_rejected(self):
        case=copy.deepcopy(after);case['planted_surface_budget_px']=7
        self.assertFalse(run(case)['isolation_pass'])
    def test_feature_fitted_normalization_is_rejected(self):
        norm=copy.deepcopy(normalization);norm['inverse_sampling_affine'][2]+=2
        self.assertFalse(run(norm=norm)['isolation_pass'])
    def test_actual_lateral_hitch_passes_only_after_repair(self):
        old=json.loads((V/'spacing-qa.json').read_text())['review'];new=json.loads((P/'spacing-qa.json').read_text())['review']
        self.assertGreater(old['maximum_lateral_backtrack_px'],10);self.assertFalse(old['recovery_key_pass'])
        self.assertEqual(new['maximum_lateral_backtrack_px'],0);self.assertTrue(new['recovery_key_pass'])
    def test_ten_pixel_head_misattachment_still_rejected(self):
        row=copy.deepcopy(after['variants']['review'][6]);row['head_matrix'][4]+=10
        passes={mode:np.array(Image.open(P/f'renders/review/{mode}/06.png').convert('RGBA')) for mode in ['full','body','head','collar']}
        self.assertFalse(neck.neck_metrics(row,after,passes)['pass_'])
    def test_actual_packed_reviewed_empty_alpha_is_zero(self):
        self.assertTrue(alpha.audit_sheet(P/'packed-reference-atlas.png')['empty_patch_pass'])
if __name__=='__main__':unittest.main(verbosity=2)
