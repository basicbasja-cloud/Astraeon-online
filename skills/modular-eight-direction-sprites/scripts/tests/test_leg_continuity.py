"""Adversarial anatomical controls, distinct from judging actual generated artwork."""
import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('leg_continuity',Path(__file__).resolve().parents[1]/'leg-continuity.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)

class LegContinuityTests(unittest.TestCase):
    def case(self):
        c=qa.init_case(ROOT/'research/sprite-animation/walk-test-v9/motion.json',ROOT/'research/sprite-animation/quality-review-v10/master/frames',[0,10,20,30])
        c['synthetic_coordinate_control']=True
        for f in c['frames']:
            f['identity_review']='confirmed'
            for n in qa.JOINTS:f['points'][n]={'xy':f['reference'][n].copy(),'visibility':'observed','uncertainty_px':0.}
        return c
    def test_actual_source_cycle_and_crossing_have_no_false_swap(self):
        c=self.case();r=qa.analyze(c)
        self.assertEqual(r['status'],'SCOPED_2D_MEASUREMENTS_WITHIN_BUDGET')
        self.assertEqual(r['observed_coverage_percent'],100)
        self.assertTrue(all(x['residual_px_per_s']<1e-8 for x in r['transitions']))
        self.assertTrue(r['transitions'][-1]['includes_loop_seam'])
        self.assertFalse(r['release_ready'])
    def swap(self,c,k):
        f=c['frames'][k];old=copy.deepcopy(f['points'])
        f['points']={n:old[qa.other(n)] for n in qa.JOINTS}
    def test_complete_leg_swap_is_flagged(self):
        c=self.case();self.swap(c,1);r=qa.analyze(c)
        self.assertIn('possible_leg_label_or_pose_swap',r['frames'][1]['flags'])
        self.assertTrue(any('next_pose_side_exchange_fits_better' in e['flags'] for e in r['transitions']))
    def test_loop_boundary_is_not_skipped(self):
        c=self.case();self.swap(c,3);r=qa.analyze(c)
        self.assertIn('trajectory_residual_jump',r['transitions'][-1]['flags'])
    def test_partial_ankle_swap_is_flagged(self):
        c=self.case();f=c['frames'][0];a=f['points']['ankle_r'];f['points']['ankle_r']=f['points']['ankle_l'];f['points']['ankle_l']=a
        self.assertIn('source_pose_deviation',qa.analyze(c)['frames'][0]['flags'])
    def test_knee_spike_is_flagged(self):
        c=self.case();c['frames'][1]['points']['knee_r']['xy'][0]+=160
        self.assertIn('source_pose_deviation',qa.analyze(c)['frames'][1]['flags'])
    def test_repeating_first_half_pose_fails_source_comparison(self):
        c=self.case();c['frames'][2]['points']=copy.deepcopy(c['frames'][0]['points'])
        self.assertIn('source_pose_deviation',qa.analyze(c)['frames'][2]['flags'])
    def test_screen_mirror_is_not_an_anatomical_turn(self):
        c=self.case()
        for f in c['frames']:
            for p in f['points'].values():p['xy'][0]=511-p['xy'][0]
        self.assertTrue(any('source_pose_deviation' in f['flags'] for f in qa.analyze(c)['frames']))
    def test_occluded_hip_blocks_measurement_and_pass(self):
        c=self.case();c['frames'][0]['points']['hip_l']={'xy':None,'visibility':'unknown','uncertainty_px':0.}
        r=qa.analyze(c);self.assertEqual(r['status'],'REVIEW_REQUIRED')
        self.assertIsNone(r['frames'][0]['claimed_identity_rmse_px'])
        self.assertLess(r['observed_coverage_percent'],100)
    def test_uncertain_identity_never_becomes_anatomy_pass(self):
        c=self.case();c['frames'][0]['identity_review']='unconfirmed'
        self.assertEqual(qa.analyze(c)['status'],'REVIEW_REQUIRED')
    def test_large_uncertainty_keeps_raw_error_visible(self):
        c=self.case();p=c['frames'][0]['points']['knee_r'];p['xy'][0]+=100;p['uncertainty_px']=150
        r=qa.analyze(c)
        self.assertGreater(r['frames'][0]['claimed_identity_raw_rmse_px'],16)
        self.assertIn('source_pose_difference_inside_annotation_uncertainty',r['frames'][0]['flags'])
    def test_tampered_bone_projection_is_rejected(self):
        c=self.case();c['frames'][0]['reference']['knee_r'][0]+=1
        with self.assertRaisesRegex(ValueError,'Modified bone'):qa.validate_case(c,True)
    def test_stale_image_is_rejected(self):
        c=self.case();c['frames'][0]['image_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Stale image'):qa.validate_case(c,True)
    def test_source_time_tampering_is_rejected(self):
        c=self.case();c['frames'][1]['time_seconds']+=.001
        with self.assertRaisesRegex(ValueError,'Wrong source pose time'):qa.validate_case(c,True)
    def test_baked_rig_hash_is_verified(self):
        c=self.case();c['source_blend_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Stale baked rig'):qa.validate_case(c,True)
    def test_sparse_intervals_are_measured_on_source_clock(self):
        c=self.case();r=qa.analyze(c)
        self.assertAlmostEqual(sum(e['dt_seconds'] for e in r['transitions']),c['duration_seconds'])
        self.assertTrue(all(e['dt_seconds']>0 for e in r['transitions']))
    def test_native_size_has_proportional_budgets(self):
        c=qa.init_case(ROOT/'research/sprite-animation/walk-test-v9/motion.json',ROOT/'research/sprite-animation/walk-test-v9/rig-preview/frames/SE',[0,5,10,15])
        self.assertEqual(c['thresholds']['pose_px'],4)
        self.assertEqual(c['thresholds']['swap_margin_px'],2)
    def test_wrong_facing_is_not_silently_compared_to_SE(self):
        c=self.case();c['facing']='INVALID'
        with self.assertRaisesRegex(ValueError,'Unsupported facing'):qa.analyze(c)
    def test_all_eight_physical_facings_preserve_source_anatomy(self):
        for view in qa.FACINGS:
            c=qa.init_case(ROOT/'research/sprite-animation/walk-test-v9/motion.json',ROOT/'research/sprite-animation/quality-review-v10/master/frames',[0,10,20,30],view)
            for f in c['frames']:
                f['identity_review']='confirmed'
                for n in qa.JOINTS:f['points'][n]={'xy':f['reference'][n].copy(),'visibility':'observed','uncertainty_px':0.}
            self.assertEqual(qa.analyze(c)['status'],'SCOPED_2D_MEASUREMENTS_WITHIN_BUDGET',view)
    def test_facing_change_with_old_reference_is_rejected(self):
        c=self.case();c['facing']='N'
        with self.assertRaisesRegex(ValueError,'Modified bone reference'):qa.validate_case(c,True)
    def test_partial_chain_swap_is_visible_despite_large_uncertainty(self):
        c=self.case();f=c['frames'][0];old=copy.deepcopy(f['points'])
        for n in qa.JOINTS:
            if n.startswith('knee'):f['points'][n]=old[qa.other(n)]
            f['points'][n]['uncertainty_px']=200
        r=qa.analyze(c)
        self.assertIn('mixed_or_exchanged_leg_association_fits_better_raw',r['frames'][0]['flags'])
        self.assertIn('knee',r['frames'][0]['best_counterfactual_component_association']['exchanged_components'])
    def test_projected_overlapping_knees_do_not_get_false_certainty(self):
        c=self.case()
        for n in ['knee_r','knee_l']:c['frames'][1]['points'][n]['uncertainty_px']=20
        r=qa.analyze(c)
        self.assertIn('projected_side_pair_ambiguous:knee',r['frames'][1]['flags'])
        self.assertEqual(r['status'],'REVIEW_REQUIRED')
    def test_exactly_coincident_knees_are_ambiguous_even_with_zero_uncertainty(self):
        c=self.case();f=c['frames'][1]
        f['reference']['knee_l']=f['reference']['knee_r'].copy()
        f['points']['knee_l']['xy']=f['points']['knee_r']['xy'].copy()
        f['points']['knee_r']['uncertainty_px']=f['points']['knee_l']['uncertainty_px']=0.
        self.assertIn('projected_side_pair_ambiguous:knee',qa.analyze(c)['frames'][1]['flags'])

if __name__=='__main__':unittest.main()
