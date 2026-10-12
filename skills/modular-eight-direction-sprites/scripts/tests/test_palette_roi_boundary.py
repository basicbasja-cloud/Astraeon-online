import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
loader=importlib.util.spec_from_file_location('continuity',ROOT/'skills/modular-eight-direction-sprites/scripts/walk-continuity.py')
m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)


class RoiBoundaryTests(unittest.TestCase):
    def test_actual_clipped_hair_region_is_inconclusive(self):
        p=ROOT/'research/sprite-animation/reverse-paintover-v19/evidence/valyria-keys-continuity-input.json'
        s=json.loads(p.read_text());s['palette_patch_probe']['roi']=[80,70,330,240]
        r=m.palette_patch_probe(s)
        self.assertEqual(r['status'],'INCONCLUSIVE')
        self.assertTrue(any(f['status']=='INCONCLUSIVE_REGION_TOUCHES_ROI' for f in r['frames']))
        self.assertNotIn('max_centroid_step_px',r)
    def test_whole_clip_calibrated_roi_keeps_scoped_measurement(self):
        p=ROOT/'research/sprite-animation/reverse-paintover-v19/evidence/valyria-keys-continuity-input.json'
        r=m.palette_patch_probe(json.loads(p.read_text()))
        self.assertEqual(r['status'],'DECLARED_PALETTE_REGION_MEASURED')
        self.assertFalse(r['anatomy_pass']);self.assertFalse(r['art_modified'])


if __name__=='__main__':unittest.main()
