import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
import shutil

import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location('walk_continuity', Path(__file__).parents[1] / 'walk-continuity.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WalkContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        p = Path(self.temp.name) / 'frame.png'
        Image.new('RGBA', (32, 32), 'red').save(p)
        self.spec = {'label': 'control', 'canvas': [32, 32], 'tracked_landmarks': ['eye'], 'frames': [
            {'image': str(p), 'sha256': m.sha(p), 'duration_ms': 100,
             'landmarks': {'eye': {'xy': [x, 8], 'uncertainty_px': 1},
                           'ankle_a': {'xy': [x, 20], 'uncertainty_px': 2},
                           'ankle_b': {'xy': [25-x, 20], 'uncertainty_px': 2}}}
            for x in [4, 5, 20]]}

    def tearDown(self):
        self.temp.cleanup()

    def test_last_to_first_is_not_omitted(self):
        r = m.audit(self.spec)
        self.assertEqual(r['landmarks']['eye']['last_to_first_step_px'], 16)
        self.assertEqual(r['edges'][-1]['to'], 0)
        self.assertTrue(r['edges'][-1]['loop_seam'])

    def test_nonuniform_exposures_change_velocity(self):
        _, v, a = m.cyclic_differences([[0, 0], [10, 0], [20, 0]], [100, 200, 400])
        np.testing.assert_allclose(v[:, 0], [100, 50, -50])
        np.testing.assert_allclose(a[:, 0], [600, -50/.15, -100/.3])

    def test_unordered_feet_never_get_identity_trajectories(self):
        r = m.audit(self.spec)
        self.assertFalse(r['landmarks']['ankle_a']['trajectory_computed'])
        self.assertNotIn('velocity_px_per_s', r['landmarks']['ankle_a'])
        self.assertFalse(r['semantic_leg_identity_checked'])

    def test_swapping_unordered_samples_does_not_change_span(self):
        a = m.audit(self.spec)['unordered_ankle_span_px']
        b = copy.deepcopy(self.spec)
        for f in b['frames']:
            f['landmarks']['ankle_a'], f['landmarks']['ankle_b'] = f['landmarks']['ankle_b'], f['landmarks']['ankle_a']
        self.assertEqual(a, m.audit(b)['unordered_ankle_span_px'])

    def test_missing_observation_stays_incomplete(self):
        self.spec['frames'][1]['landmarks']['eye'] = None
        r = m.audit(self.spec)
        self.assertEqual(r['landmarks']['eye']['status'], 'INCOMPLETE_OBSERVATIONS')
        self.assertNotIn('max_step_px', r['landmarks']['eye'])

    def test_tampered_image_invalidates_observations(self):
        Image.new('RGBA', (32, 32), 'green').save(self.spec['frames'][0]['image'])
        with self.assertRaisesRegex(ValueError, 'Changed artwork'):
            m.audit(self.spec)

    def test_invalid_clock_rejected_even_without_tracked_points(self):
        self.spec['tracked_landmarks'] = []
        for bad in [0, -1, float('nan')]:
            self.spec['frames'][0]['duration_ms'] = bad
            with self.assertRaises(ValueError):
                m.audit(self.spec)

    def test_static_visible_points_do_not_approve_motion(self):
        for f in self.spec['frames']:
            f['landmarks']['eye']['xy'] = [8, 8]
        r = m.audit(self.spec)
        self.assertEqual(r['landmarks']['eye']['max_step_px'], 0)
        self.assertFalse(r['contact_lock_checked'])
        self.assertEqual(r['status'], 'DIAGNOSTIC_REQUIRES_VISUAL_REVIEW')

    def test_coordinate_uncertainty_is_not_accuracy_probability(self):
        r = m.audit(self.spec)
        self.assertEqual(r['landmarks']['eye']['uncertainty_adjusted_step_px'], [0, 13, 14])
        self.assertNotIn('accuracy', r)

    def test_out_of_canvas_rejected(self):
        self.spec['frames'][0]['landmarks']['eye']['xy'] = [32, 3]
        with self.assertRaisesRegex(ValueError, 'Invalid visible'):
            m.audit(self.spec)

    def test_new_character_template_starts_unknown_and_refuses_overwrite(self):
        directory=Path(self.temp.name)/'frames';directory.mkdir()
        for i in range(3):shutil.copyfile(self.spec['frames'][0]['image'],directory/f'{i:02}.png')
        out=Path(self.temp.name)/'template.json'
        command=[sys.executable,str(Path(m.__file__)), '--init-from-frames',str(directory), '--frame-ms','110', '--out',str(out)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(out.read_text());self.assertEqual(len(data['frames']),3)
        self.assertTrue(all(f['duration_ms']==110 and all(v is None for v in f['landmarks'].values()) for f in data['frames']))
        self.assertEqual(m.audit(data)['landmarks']['root']['status'],'INCOMPLETE_OBSERVATIONS')
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_actual_user_failure_and_candidate_are_measured_separately(self):
        root = Path(__file__).resolve().parents[4]
        # Run repository tests from its root: bound image paths deliberately are not guessed.
        evidence = root / 'research/sprite-animation/continuity-v14/evidence'
        old = m.audit(json.loads((evidence/'v13-observations.json').read_text()))
        new = m.audit(json.loads((evidence/'v14-observations.json').read_text()))
        self.assertGreater(old['landmarks']['eye']['max_step_px'], 45)
        self.assertLess(new['landmarks']['eye']['max_step_px'], 12)
        self.assertFalse(new['semantic_leg_identity_checked'])
        self.assertFalse(new['art_pixels_modified'])

    @unittest.skipUnless(importlib.util.find_spec('cv2'), 'OpenCV feature diagnostic requires pinned optional dependency')
    def test_actual_low_feature_matches_remain_inconclusive(self):
        evidence=Path(__file__).resolve().parents[4]/'research/sprite-animation/continuity-v14/evidence'
        old=m.audit(json.loads((evidence/'v13-observations.json').read_text()))['image_patch_tracking']
        new=m.audit(json.loads((evidence/'v14-observations.json').read_text()))['image_patch_tracking']
        self.assertEqual(old['status'],'INCONCLUSIVE')
        self.assertEqual(new['status'],'INCONCLUSIVE')
        self.assertNotIn('max_center_step_px',old)
        self.assertNotIn('max_center_step_px',new)
        self.assertFalse(new['anatomy_pass'])

    @unittest.skipUnless(importlib.util.find_spec('cv2'), 'OpenCV palette probe requires pinned optional dependency')
    def test_actual_palette_region_flags_old_placement_without_warp(self):
        evidence=Path(__file__).resolve().parents[4]/'research/sprite-animation/continuity-v14/evidence'
        old=m.audit(json.loads((evidence/'v13-observations.json').read_text()))['palette_patch_probe']
        new=m.audit(json.loads((evidence/'v14-observations.json').read_text()))['palette_patch_probe']
        self.assertTrue(old['registration_warning'])
        self.assertFalse(new['registration_warning'])
        self.assertGreater(old['max_centroid_step_px'],45)
        self.assertLess(new['max_centroid_step_px'],15)
        self.assertFalse(new['art_modified'])
        self.assertFalse(new['anatomy_pass'])


if __name__ == '__main__':
    unittest.main()
