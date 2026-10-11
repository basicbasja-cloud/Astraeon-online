"""Meaningful geometry failure fixtures for the bounded source-preset experiment."""
import math
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'studies/source-motion'))
from retarget_math import fk, two_segment

class RetargetTests(unittest.TestCase):
    def test_fk_parent_rotation_precedes_edge_translation(self):
        root = np.eye(4); root[:2,:2] = [[0,-1],[1,0]]; root[0,3] = 3
        child = np.eye(4); child[0,3] = 2
        result = fk({'root':{'parent':None},'hand_r':{'parent':'root'}},
                    {'root':root,'hand_r':child},{'root':1,'hand_r':.5},np.eye(4))
        np.testing.assert_allclose(result['hand_r'][:3,3],[3,1,0],atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(result['hand_r'][:3,:3]),1)

    def test_fk_rejects_incomplete_hierarchy_scale_and_reflection(self):
        r={'root':{'parent':None}}; m={'root':np.eye(4)}
        with self.assertRaises(ValueError):fk(r,{}, {'root':1},np.eye(4))
        with self.assertRaises(ValueError):fk({'root':{'parent':'missing'}},m,{'root':1},np.eye(4))
        with self.assertRaises(ValueError):fk({'root':{'parent':'root'}},m,{'root':1},np.eye(4))
        for bad in [0,-1,float('nan')]:
            with self.assertRaises(ValueError):fk(r,m,{'root':bad},np.eye(4))
        for x in [-1,2]:
            a=np.eye(4);a[0,0]=x
            with self.assertRaises(ValueError):fk(r,{'root':a},{'root':1},np.eye(4))

    def test_reachable_goal_keeps_lengths_and_bend_half_plane(self):
        for sign in [-1,1]:
            r=two_segment([0,0,0],[0,sign,0],[1,0,0],1,1)
            self.assertTrue(r['reachable']);self.assertLess(r['residual'],1e-12)
            self.assertAlmostEqual(np.linalg.norm(r['middle']),1)
            self.assertAlmostEqual(np.linalg.norm(r['end']-r['middle']),1)
            self.assertGreater(r['middle'][1]*sign,0)

    def test_object_transform_cannot_silently_mirror_anatomical_sides(self):
        mirror=np.eye(4);mirror[0,0]=-1
        with self.assertRaises(ValueError):
            fk({'root':{'parent':None}}, {'root':np.eye(4)}, {'root':1}, mirror)

    def test_unreachable_goal_is_exposed_without_stretch(self):
        r=two_segment([0,0,0],[0,1,0],[3,0,0],1,1)
        self.assertFalse(r['reachable']);self.assertAlmostEqual(r['residual'],1)
        np.testing.assert_allclose(r['end'],[2,0,0])
        self.assertAlmostEqual(np.linalg.norm(r['middle']),1)
        self.assertAlmostEqual(np.linalg.norm(r['end']-r['middle']),1)

    def test_goal_inside_minimum_reach_is_not_false_success(self):
        r=two_segment([0,0,0],[0,1,0],[.25,0,0],2,1)
        self.assertFalse(r['reachable']);self.assertAlmostEqual(r['residual'],.75)
        self.assertAlmostEqual(np.linalg.norm(r['middle']),2)
        self.assertAlmostEqual(np.linalg.norm(r['end']-r['middle']),1)

    def test_unknown_bend_or_invalid_input_requires_authored_guide(self):
        for base,pole,goal,a,b in [([0,0,0],[1,0,0],[2,0,0],1,1),
                                   ([0,0,0],[0,1,0],[0,0,0],1,1),
                                   ([0,0,0],[0,1,0],[1,0,0],0,1),
                                   ([0,0,0],[0,1,0],[math.nan,0,0],1,1)]:
            with self.assertRaises(ValueError):two_segment(base,pole,goal,a,b)

if __name__=='__main__':unittest.main()
