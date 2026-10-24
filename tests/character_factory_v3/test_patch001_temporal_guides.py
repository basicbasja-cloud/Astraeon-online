import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from audit_patch001_temporal_guides import temporal_view


def row(x,tip=None):
    return {'action':'Hold','landmarks':{'pelvis':[x,10],'head':[x,5]},'weapon_guide':{'grip':[x,8],'tip':[x if tip is None else tip,1]}}


class TemporalGuideTests(unittest.TestCase):
    def test_partial_guard_recovery_loop_is_flagged(self):
        result=temporal_view([row(x)for x in [0,1,2,3]],240,True)
        self.assertTrue(result['suspected_loop_reset']);self.assertEqual(result['loop_seam']['maximum_runtime_px'],3)

    def test_ordinary_cycle_has_a_normal_closing_step(self):
        result=temporal_view([row(x)for x in [0,1,2,1]],240,True)
        self.assertFalse(result['suspected_loop_reset'])

    def test_sustained_native_guard_has_zero_seam(self):
        result=temporal_view([row(10)for _ in range(16)],1536,True)
        self.assertFalse(result['suspected_loop_reset']);self.assertEqual(result['loop_seam']['maximum_runtime_px'],0)

    def test_one_shot_recovery_is_not_judged_as_a_loop(self):
        result=temporal_view([row(0),row(1),row(20)],240,False)
        self.assertFalse(result['suspected_loop_reset']);self.assertIsNone(result['loop_seam']);self.assertTrue(result['first_to_last_for_nonloop_is_not_a_seam'])

    def test_weapon_tip_is_checked_even_with_fixed_body(self):
        result=temporal_view([row(0,x)for x in [0,1,2,3]],240,True)
        self.assertTrue(result['suspected_loop_reset']);self.assertEqual(result['loop_seam']['points_runtime_px']['weapon_tip'],3)

    def test_nonfinite_points_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid source screen point'):temporal_view([row(0),row(float('nan'))],240,True)
        with self.assertRaisesRegex(ValueError,'resolution'):temporal_view([row(0),row(1)],0,True)


if __name__=='__main__':unittest.main()
