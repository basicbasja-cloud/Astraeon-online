import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SCRIPT=ROOT/'skills/modular-eight-direction-sprites/scripts/reference-truth.py'
loader=importlib.util.spec_from_file_location('truth',SCRIPT)
m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
CASE=ROOT/'research/sprite-animation/reverse-paintover-v19/evidence/ro-sixteen-truth-contract.json'


class TruthTests(unittest.TestCase):
    def setUp(self):self.case=json.loads(CASE.read_text())
    def test_real_locked_keys_keep_evidence_and_production_separate(self):
        r=m.audit(self.case,ROOT)
        self.assertEqual((r['captured_exposures'],r['authored_inbetweens']),(8,8))
        self.assertFalse(r['production_ready']);self.assertFalse(r['hidden_skeleton_recovered'])
    def test_converter_clock_cannot_be_replaced_by_claimed_client_clock(self):
        self.case['observed_frames'][1]['duration_ms']=72
        with self.assertRaisesRegex(ValueError,'clock'):m.audit(self.case,ROOT)
    def test_inbetween_cannot_replace_locked_endpoint_even_if_hash_resealed(self):
        self.case['experiment']['sequence'][0].update(self.case['experiment']['sequence'][1])
        self.case['experiment']['sequence'][0].update(role='authored_key',source_index=0,time_ms=0)
        with self.assertRaisesRegex(ValueError,'Protected'):m.audit(self.case,ROOT)
    def test_wrap_pair_must_point_to_actual_first_key(self):
        self.case['experiment']['sequence'][-1]['source_pair']=[7,2]
        with self.assertRaisesRegex(ValueError,'Inbetween'):m.audit(self.case,ROOT)
    def test_no_hidden_truth_from_pixels(self):
        self.case['recovered_hidden_skeleton']=True
        with self.assertRaisesRegex(ValueError,'hidden skeleton'):m.audit(self.case,ROOT)
    def test_hidden_point_cannot_be_promoted_to_visible(self):
        self.case['observations']=[{'kind':'visible_surface','frame_index':0,
            'image_sha256':self.case['observed_frames'][0]['sha256'],
            'visibility':'occluded','uncertainty_px':2}]
        with self.assertRaisesRegex(ValueError,'Hidden point'):m.audit(self.case,ROOT)
    def test_source_known_bone_is_not_allowed_without_real_rig_evidence(self):
        self.case['observations']=[{'kind':'source_known_bone'}]
        with self.assertRaisesRegex(ValueError,'bone evidence'):m.audit(self.case,ROOT)
    def test_authored_clock_cannot_have_hole(self):
        self.case['experiment']['sequence'][5]['time_ms']+=10
        with self.assertRaisesRegex(ValueError,'gap/overlap'):m.audit(self.case,ROOT)
    def test_require_production_fails_closed_for_real_art(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            r=subprocess.run([sys.executable,str(SCRIPT),'--contract',str(CASE),
                '--root',str(ROOT),'--out',td+'/report.json','--require-production'],capture_output=True)
            self.assertEqual(r.returncode,2);self.assertTrue(Path(td+'/report.json').exists())
    def test_same_cycle_cannot_hide_moved_midpoint_phase(self):
        self.case['experiment']['sequence'][0]['duration_ms']=20
        self.case['experiment']['sequence'][1].update(time_ms=20,duration_ms=55)
        with self.assertRaisesRegex(ValueError,'phase moved'):m.audit(self.case,ROOT)


if __name__=='__main__':unittest.main()
