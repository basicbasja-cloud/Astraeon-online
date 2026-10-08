"""Mechanical checks for the authoring rig, not a painted visual approval."""
import importlib.util
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('walk_cycle', ROOT/'tools/swordsman-walk-cycle.py')
cycle = importlib.util.module_from_spec(spec); spec.loader.exec_module(cycle)


class ArticulatedHumanWalk(unittest.TestCase):
    def test_fixed_lengths_forward_knees_and_no_airborne_stance(self):
        for i in range(800):
            p = cycle.pose(i/800)
            self.assertTrue(any(f['stance'] for f in p['feet'].values()))
            for side, f in p['feet'].items():
                for suffix, expected in [('femur', cycle.FEMUR), ('tibia', cycle.TIBIA), ('foot', cycle.FOOT_LENGTH)]:
                    a, b = p['bones'][side+'-'+suffix]
                    self.assertAlmostEqual(float(np.linalg.norm(b-a)), expected, places=10)
                self.assertAlmostEqual(float(np.linalg.norm(f['toe']-f['heel'])), cycle.FOOT_LENGTH, places=10)
                self.assertGreater(f['poleDot'], 0, 'Anatomical knee pole must never invert')
                self.assertGreaterEqual(min(f['heel'][2], f['toe'][2]), -1e-12)
                if f['stance']:
                    self.assertAlmostEqual(float(f[f['contactKind']][2]), 0., places=10)
                    if f['contactKind'] == 'sole':
                        self.assertLess(f['kneeFlexDegrees'], 17., 'Loaded sole stance must extend, not crouch')

    def test_world_contact_is_planted_with_rigid_heel_sole_toe_roll(self):
        points = {}
        for i in range(1601):
            phase = i/800
            p = cycle.pose(phase)
            for side, f in p['feet'].items():
                if not f['stance']: continue
                key = (side, int(np.floor(phase+(0. if side == 'R' else .5))), f['contactKind'])
                world = f[f['contactKind']]+np.array((0., phase*cycle.CYCLE_DISTANCE, 0.))
                if key in points: np.testing.assert_allclose(world, points[key], atol=1e-10)
                else: points[key] = world

    def test_swing_clearance_weight_transfer_and_cycle_continuity(self):
        for side in ('R', 'L'):
            feet = [cycle.pose(i/800)['feet'][side] for i in range(800)]
            self.assertGreater(max(f['clearance'] for f in feet), .06)
            self.assertLess(max(f['clearance'] for f in feet), .075, 'Walk must not become a high-step run')
            self.assertGreater(max(f['kneeFlexDegrees'] for f in feet if not f['stance']), 40.)
        self.assertGreater(cycle.pose(.25)['pelvis'][0], 0)
        self.assertLess(cycle.pose(.75)['pelvis'][0], 0)
        self.assertEqual(cycle.pose(.25)['supportWeights'], {'R': 1., 'L': 0.})
        self.assertEqual(cycle.pose(.75)['supportWeights'], {'R': 0., 'L': 1.})
        self.assertLess(abs(cycle.pose(.25)['pelvis'][2]-cycle.pose(.0)['pelvis'][2]), .025)
        epsilon = 1e-6
        for phase in (0., cycle.DUTY, .5, cycle.DUTY-.5):
            a, b = cycle.pose(phase-epsilon), cycle.pose(phase+epsilon)
            for side in ('R', 'L'):
                self.assertLess(float(np.linalg.norm(a['feet'][side]['ankle']-b['feet'][side]['ankle'])), 1e-5)
            self.assertLess(float(np.linalg.norm(a['pelvis']-b['pelvis'])), 1e-5)

    def test_eight_phases_alternate_contacts_and_are_distinct(self):
        poses = [cycle.pose(i/8) for i in range(8)]
        self.assertEqual(poses[0]['feet']['R']['contactKind'], 'heel')
        self.assertEqual(poses[4]['feet']['L']['contactKind'], 'heel')
        self.assertTrue(poses[2]['feet']['R']['stance'])
        self.assertFalse(poses[2]['feet']['L']['stance'])
        self.assertTrue(poses[6]['feet']['L']['stance'])
        self.assertFalse(poses[6]['feet']['R']['stance'])
        for i, p in enumerate(poses):
            a = np.concatenate([p['feet'][s]['ankle'] for s in ('R', 'L')])
            for q in poses[i+1:]:
                b = np.concatenate([q['feet'][s]['ankle'] for s in ('R', 'L')])
                self.assertGreater(float(np.linalg.norm(a-b)), .025)

    def test_thigh_extends_behind_the_pelvis_before_it_passes_forward(self):
        # Planting alone previously passed a cycle in which BOTH knees stayed
        # in front of the hip. Check anatomical thigh extension independently.
        for side, offset in [('R', 0.), ('L', .5)]:
            trailing = cycle.pose((.375-offset) % 1.)['feet'][side]
            self.assertTrue(trailing['stance'])
            self.assertLess(trailing['knee'][1]-trailing['hip'][1], -.025,
                            'Late supporting thigh must extend behind the pelvis')
            backswing = cycle.pose((.625-offset) % 1.)['feet'][side]
            self.assertFalse(backswing['stance'])
            self.assertLess(backswing['knee'][1]-backswing['hip'][1], -.025,
                            'Rear foot must lift behind the pelvis before passing forward')
            passing = cycle.pose((.75-offset) % 1.)['feet'][side]
            self.assertGreater(passing['knee'][1]-passing['hip'][1], .04)


class PaintedSurfaceRegistration(unittest.TestCase):
    def test_foreshortened_foot_stays_local_to_the_anatomical_joint(self):
        from PIL import Image
        spec = importlib.util.spec_from_file_location('painted_authoring', ROOT/'tools/build-swordsman-production.py')
        painter = importlib.util.module_from_spec(spec); spec.loader.exec_module(painter)
        texture = Image.new('RGBA', (320, 320), (210, 150, 105, 255))
        for displacement in (0., .001, .5):
            surface = painter.painted_skin(texture, (150, 240), (150, 250),
                                           (150, 260), (150, 260+displacement), 3, 3)
            bounds = surface.getchannel('A').getbbox()
            self.assertIsNotNone(bounds)
            self.assertGreaterEqual(bounds[0], 146)
            self.assertLessEqual(bounds[2], 155)
            self.assertGreaterEqual(bounds[1], 256)
            self.assertLessEqual(bounds[3], 265)


class ArticulatedRun(unittest.TestCase):
    def test_run_retains_fixed_anatomy_and_planted_support_with_airborne_transfer(self):
        spec = importlib.util.spec_from_file_location('run_cycle', ROOT/'tools/swordsman-run-cycle.py')
        run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
        contacts = {}; airborne = 0
        for i in range(1601):
            phase = i/800
            p = run.pose(phase)
            airborne += not any(f['stance'] for f in p['feet'].values())
            for side, f in p['feet'].items():
                self.assertGreater(f['poleDot'], 0)
                self.assertGreaterEqual(min(f['heel'][2], f['toe'][2]), -1e-12)
                for suffix, expected in [('femur', run.FEMUR), ('tibia', run.TIBIA), ('foot', run.FOOT_LENGTH)]:
                    a, b = p['bones'][side+'-'+suffix]
                    self.assertAlmostEqual(float(np.linalg.norm(b-a)), expected, places=10)
                if f['stance']:
                    key = (side, int(np.floor(phase+(0. if side == 'R' else .5))), f['contactKind'])
                    contact = f[f['contactKind']]+np.array((0., phase*run.CYCLE_DISTANCE, 0.))
                    if key in contacts: np.testing.assert_allclose(contact, contacts[key], atol=1e-10)
                    else: contacts[key] = contact
        self.assertGreater(airborne/1601, .14)
        self.assertLess(airborne/1601, .18)
        self.assertLess(run.CYCLE_SECONDS, cycle.CYCLE_SECONDS)
        self.assertGreater(max(run.pose(i/800)['feet']['R']['clearance'] for i in range(800)), .14)


if __name__ == '__main__': unittest.main()
