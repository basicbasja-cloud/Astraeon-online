"""Actual-image negative controls. Passing tests do not approve candidate motion."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
spec = importlib.util.spec_from_file_location('review', ROOT/'skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
D = json.loads((P/'motion-contract.json').read_text())
S = json.loads((ROOT/D['source']['path']).read_text())


class ActualImageControls(unittest.TestCase):
    def setUp(self):
        self.row = copy.deepcopy(D['variants']['review'][3])
        self.images = {mode: np.array(Image.open(P/f'renders/review/{mode}/03.png').convert('RGBA'))
                       for mode in ['full', 'body', 'head', 'collar']}

    def test_actual_attached_head_passes(self):
        self.assertTrue(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_ten_pixel_misattachment_rejected(self):
        self.row['head_matrix'][4] += 10
        self.assertFalse(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_gap_in_actual_render_rejected(self):
        self.images['full'][:, :, 3] = 0
        self.assertFalse(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_declared_attachment_without_head_pixels_rejected(self):
        self.images['head'][:, :, 3] = 0
        self.assertFalse(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_missing_collar_foreground_rejected(self):
        self.images['collar'][:, :, 3] = 0
        self.assertFalse(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_wrong_collar_pixels_rejected(self):
        mask = self.images['collar'][:, :, 3] == 255
        self.images['full'][mask, 0] ^= 64
        self.assertFalse(review.neck_metrics(self.row, D, self.images)['pass_'])

    def test_reflected_head_not_uniform_positive(self):
        self.assertFalse(review.uniform_positive([-.11, 0, 0, .11, 0, 0], .11))

    def test_anisotropic_head_not_uniform(self):
        self.assertFalse(review.uniform_positive([.11, 0, 0, .12, 0, 0], .11))

    def test_empty_support_is_unknown_not_pass(self):
        with self.assertRaises(ValueError):
            review.extrema(np.zeros((512, 384, 4), dtype=np.uint8), [10, 10, 20, 20])

    def test_native_recovery_overshoot_is_caught(self):
        self.assertFalse(review.phase_metrics(D['variants']['raw8'], S, D)['pass_'])
        self.assertTrue(review.phase_metrics(D['variants']['review'], S, D)['pass_'])

    def test_real_contact_failure_not_rounded_away(self):
        report = review.audit(D, ROOT, P/'renders')
        far = report['variants']['review']['support']['far']
        self.assertGreater(far['raw_range_at_display_scale_px'][0], 6)
        self.assertLessEqual(far['rendered_range_px'][0], 6)
        self.assertFalse(report['variants']['review']['contact_pass'])
        self.assertFalse(report['variants']['review']['motion_metrics_pass'])

    def test_hash_bound_wrong_body_is_rejected(self):
        changed = copy.deepcopy(D)
        changed['variants']['review'][3]['body']['path'] = D['variants']['review'][2]['body']['path']
        report = review.audit(changed, ROOT, P/'renders')
        self.assertFalse(report['integrity_checks']['input_hashes'])
        self.assertFalse(report['variants']['review']['exact_raw_grid_crops'])
        self.assertFalse(report['variants']['review']['motion_metrics_pass'])

    def test_per_frame_body_registration_is_rejected(self):
        changed = copy.deepcopy(D)
        changed['variants']['review'][3]['body_matrix'][4] += 8
        self.assertFalse(review.audit(changed, ROOT, P/'renders')['variants']['review']['common_body_transform'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
