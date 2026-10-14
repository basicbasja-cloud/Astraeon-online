"""Real prior errors plus focused controls; no test grants new artwork approval."""
import copy,importlib.util,json
from pathlib import Path
import unittest

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
spacing=module('spacing','skills/modular-eight-direction-sprites/scripts/coherent-motion-spacing.py')
alpha=module('alpha','skills/modular-eight-direction-sprites/scripts/coherent-strip-alpha.py')
edit=module('edit','skills/modular-eight-direction-sprites/scripts/native-strip-edit-audit.py')
D=json.loads((P/'motion-contract.json').read_text());S=json.loads((ROOT/D['source']['path']).read_text());Q=json.loads((P/'motion-qa.json').read_text())
old=json.loads((P.parent/'neck-motion-v36/motion-contract.json').read_text());oldq=json.loads((P.parent/'neck-motion-v36/motion-qa.json').read_text())

class Controls(unittest.TestCase):
    def test_actual_prior_standing_substitute_is_rejected(self):
        r=spacing.audit_sequence(old['variants']['review'],S,oldq['variants']['review']['support'])
        self.assertFalse(r['penultimate_body_drawing_distinct']);self.assertFalse(r['recovery_key_pass'])

    def test_real_lateral_hitch_not_hidden_by_contact_pass(self):
        rows=copy.deepcopy(D['variants']['raw8']);rows[0]=copy.deepcopy(rows[-1]);rows[0]['source_time_seconds']=0
        r=spacing.audit_sequence(rows,S,Q['variants']['raw8']['support'],lateral_monotonic_expected=True)
        self.assertTrue(r['contact_pass']);self.assertGreater(r['maximum_lateral_backtrack_px'],2);self.assertFalse(r['recovery_key_pass'])

    def test_relabelled_same_drawing_is_not_an_intermediate(self):
        rows=copy.deepcopy(D['variants']['review']);rows[6]['body']['sha256']=rows[7]['body']['sha256']
        r=spacing.audit_sequence(rows,S,Q['variants']['review']['support'],lateral_monotonic_expected=True)
        self.assertFalse(r['penultimate_body_drawing_distinct']);self.assertFalse(r['recovery_key_pass'])

    def test_distinct_image_at_rest_is_still_not_an_intermediate(self):
        rows=copy.deepcopy(D['variants']['review']);rows[6]['observed_receiver_surface_xy']=rows[7]['observed_receiver_surface_xy']
        self.assertFalse(spacing.audit_sequence(rows,S,Q['variants']['review']['support'])['penultimate_surface_strictly_between'])

    def test_no_body_action_is_unknown_not_pass(self):
        rows=copy.deepcopy(D['variants']['review'])
        for r in rows:r['observed_receiver_surface_xy']=[200,180]
        with self.assertRaises(ValueError):spacing.audit_sequence(rows,S,Q['variants']['review']['support'])

    def test_bad_source_timestamps_are_rejected(self):
        source=copy.deepcopy(S);source['frames'][2]['source_time_seconds']=0
        with self.assertRaises(ValueError):spacing.audit_sequence(D['variants']['review'],source,Q['variants']['review']['support'])

    def test_actual_clean_alpha_preserves_unseen_rgb(self):
        r=alpha.audit_sheet(P/'attempt2-raw.png')
        # Native key0 has one alpha1 speck and is unselected independently of
        # this test; source0/7 use the same actual rest7. Keep the strict limit.
        self.assertFalse(r['empty_patch_pass'])
        self.assertTrue(all(p['pass_'] for p in r['observations'] if p['art_index']!=0))
        self.assertFalse(r['source_pixels_modified'])

    def test_actual_translucent_matte_is_rejected(self):
        r=alpha.audit_sheet(P/'attempt3-raw.png');self.assertFalse(r['empty_patch_pass'])

    def test_identical_native_asset_preserves_visible_regions(self):
        self.assertTrue(edit.audit(P/'attempt2-raw.png',P/'attempt2-raw.png',[6])['unrequested_cells_preserved'])

    def test_actual_local_repair_changed_unrequested_frames(self):
        r=edit.audit(P/'attempt2-raw.png',P/'attempt3-raw.png',[6])
        self.assertFalse(r['unrequested_cells_preserved'])
        self.assertTrue(any(row['changed_opaque_region_pixels']>100 for row in r['rows'] if not row['requested_edit']))

if __name__=='__main__':unittest.main(verbosity=2)
