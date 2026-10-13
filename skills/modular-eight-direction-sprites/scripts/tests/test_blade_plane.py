import importlib.util,json,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('blade',ROOT/'skills/modular-eight-direction-sprites/scripts/blade-plane.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=ROOT/'research/sprite-animation/diagonal-blade-study-v26'
class BladePlaneTests(unittest.TestCase):
    def test_real_edge_on_source_is_not_readable_diagonal_proof(self):
        s=json.loads((P/'source-edge-on-unselected/source-index.json').read_text());r=m.audit(s,None,ROOT)
        self.assertIn('source_plane_reads_edge_on_in_declared_camera',r['issues'])
        self.assertLess(r['measurements']['minimum_source_blade_plane_view_dot'],.02)
    def test_real_v25_horizontal_finish_is_caught(self):
        s=json.loads((ROOT/'research/sprite-animation/cross-body-slash-v25/rig-source/source-index.json').read_text());r=m.audit(s,None,ROOT)
        self.assertIn('source_finish_outside_declared_SE_diagonal_band',r['issues'])
        self.assertIn('source_edge_changes_outside_declared_fixed_plane',r['issues'])
    def test_revised_actual_source_keeps_diagonal_finish_but_art_unknown(self):
        s=json.loads((P/'rig-source/source-index.json').read_text());r=m.audit(s,None,ROOT)
        self.assertEqual(r['issues'],['painted_blade_observations_unknown'])
        self.assertFalse(r['production_pass'])
    def test_rig_camera_is_part_of_plane_readability(self):
        s=json.loads((P/'rig-source/source-index.json').read_text());s['camera_matrix_world'][0][2]=0;s['camera_matrix_world'][1][2]=1;s['camera_matrix_world'][2][2]=0
        r=m.audit(s,None,ROOT);self.assertNotAlmostEqual(r['measurements']['minimum_source_blade_plane_view_dot'],.28033,places=3)
    def test_actual_clipped_generated_sword_does_not_get_a_fake_tip(self):
        s=json.loads((P/'rig-source/source-index.json').read_text());a=json.loads((P/'evidence/visible-blade-case.json').read_text());r=m.audit(s,a,ROOT)
        self.assertIn('raw_pose_cell_clipping_or_spill',r['issues'])
        self.assertIn('painted_blade_observation_unknown',r['issues'])
        self.assertNotIn(4,[x['key'] for x in r['painted_observations']])
    def test_actual_v27_grip_basis_changes_hand_axes_but_keeps_blade_plane(self):
        s=json.loads((ROOT/'research/sprite-animation/weighted-slash-v27/rig-source/source-index.json').read_text());r=m.audit(s,None,ROOT)
        self.assertEqual(r['issues'],['painted_blade_observations_unknown']);self.assertLess(r['measurements']['source_edge_normal_drift'],1e-5);self.assertFalse(r['production_pass'])
if __name__=='__main__':unittest.main()
