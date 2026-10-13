import importlib.util, json, unittest, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('slash',ROOT/'skills/modular-eight-direction-sprites/scripts/slash-gesture.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SlashGestureTests(unittest.TestCase):
    def setUp(self):
        self.case=json.loads((ROOT/'research/sprite-animation/stable-hand-sweep-v24/evidence/slash-gesture-case.json').read_text())
    def kinds(self,c):return {i['kind'] for i in module.audit(c,ROOT)['issues']}
    def test_actual_v24_near_duplicate_follow_is_caught(self):
        r=module.audit(self.case,ROOT)
        self.assertLess(r['measurements']['cut_to_follow_palm_distance_px'],7)
        self.assertIn('insufficient_distinct_follow_pose',self.kinds(self.case))
    def test_actual_v24_source_never_crosses_sides(self):
        self.assertIn('source_never_crosses_declared_body_side',self.kinds(self.case))
    def test_relabeling_cannot_erase_known_rejected_pixels(self):
        self.case['user_status']='UNREVIEWED'
        self.assertIn('known_rejected_pixels',self.kinds(self.case))
    def test_changed_image_binding_is_not_old_review(self):
        self.case['frames'][0]['sha256']='0'*64
        self.assertIn('binding',self.kinds(self.case))
    def test_air_annotation_is_not_visible_evidence(self):
        self.case['frames'][3]['visible_points']['palm']=[1,1]
        self.assertIn('point_not_on_foreground',self.kinds(self.case))
    def test_unknown_grip_never_becomes_production_pass(self):
        self.assertIn('unverified_grip_edge_alignment',self.kinds(self.case))
        self.assertFalse(module.audit(self.case,ROOT)['production_pass'])
    def test_actual_v25_second_attempt_remains_blocked(self):
        c=json.loads((ROOT/'research/sprite-animation/cross-body-slash-v25/evidence/attempt2-gesture-case.json').read_text())
        self.assertIn('insufficient_distinct_follow_pose',self.kinds(c))
        self.assertIn('held_out_boot_x_variation',self.kinds(c))
        self.assertNotIn('source_never_crosses_declared_body_side',self.kinds(c))
    def test_current_candidate_cannot_be_promoted_through_diagnostic_exit(self):
        with tempfile.TemporaryDirectory() as d:
            r=subprocess.run([sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/slash-gesture.py'),
                '--case',str(ROOT/'research/sprite-animation/cross-body-slash-v25/evidence/slash-gesture-case.json'),
                '--root',str(ROOT),'--out',str(Path(d)/'report.json'),'--require-production'],capture_output=True,text=True)
            self.assertEqual(r.returncode,2)
            self.assertFalse(json.loads((Path(d)/'report.json').read_text())['production_pass'])

if __name__=='__main__':unittest.main()
