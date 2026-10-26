import copy
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from repair_same_pose_recovery import equivalent_body_pose


class SamePoseRecoveryTests(unittest.TestCase):
    def pose(self):
        return {'bones': {name: {'world_matrix': np.eye(4).tolist()}
                          for name in ['pelvis', 'hand_l', 'foot_l']}}

    def test_identical_whole_skeleton_is_reusable(self):
        pose = self.pose()
        self.assertEqual(equivalent_body_pose(pose, copy.deepcopy(pose)), 0)

    def test_equal_root_does_not_allow_changed_hand(self):
        first, last = self.pose(), self.pose()
        last['bones']['hand_l']['world_matrix'][0][3] = .01
        with self.assertRaisesRegex(ValueError, 'poses differ'):
            equivalent_body_pose(first, last)

    def test_missing_bone_is_rejected(self):
        first, last = self.pose(), self.pose()
        del last['bones']['foot_l']
        with self.assertRaisesRegex(ValueError, 'skeleton differs'):
            equivalent_body_pose(first, last)

    def test_nonfinite_bone_cannot_bypass_tolerance(self):
        first, last = self.pose(), self.pose()
        last['bones']['hand_l']['world_matrix'][0][0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Invalid source'):
            equivalent_body_pose(first, last)


if __name__ == '__main__':
    unittest.main()
