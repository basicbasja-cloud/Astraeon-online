import ast
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools/character_factory_v3'
sys.path.insert(0,str(TOOLS))
from export_evaluated_guide_skeleton import replay_guide_profiles,sha

class SkeletonProfileReplayTests(unittest.TestCase):
    def job(self,gaze=False):
        result={'hero_fit_study':{'torso_length_scale':.75,'head_scale':1.3},
                'hero_fit_study_helper_sha256':sha(TOOLS/'hero_fit_guide_study.py'),
                'hero_fit_study_renderer_sha256':sha(TOOLS/'render_hero_fit_guide_study.py')}
        if gaze:
            result.update({'target_gaze_study':{'reference_head_world_quaternion':[1,0,0,0]},
                           'target_gaze_study_helper_sha256':sha(TOOLS/'target_gaze_guide_study.py'),
                           'target_gaze_study_renderer_sha256':sha(TOOLS/'render_target_gaze_guide_study.py')})
        return result

    def test_ordinary_capture_is_not_adapted(self):
        tree=ast.parse('def prop_pose():\n pass')
        self.assertIs(replay_guide_profiles(tree,{}),tree)

    def test_fit_is_replayed_before_gaze(self):
        tree=replay_guide_profiles(ast.parse('def prop_pose():\n pass'),self.job(True))
        text=ast.unparse(tree)
        self.assertLess(text.index('apply_fit(rig, job)'),text.index('apply_target_gaze(rig, job)'))

    def test_fit_only_does_not_add_gaze(self):
        text=ast.unparse(replay_guide_profiles(ast.parse('def prop_pose():\n pass'),self.job()))
        self.assertIn('apply_fit(rig, job)',text)
        self.assertNotIn('apply_target_gaze',text)

    def test_gaze_without_captured_fit_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'requires'):
            replay_guide_profiles(ast.parse('def prop_pose():\n pass'),{'target_gaze_study':{'present':True}})

    def test_stale_profile_helpers_are_rejected(self):
        for key in ['hero_fit_study_helper_sha256','target_gaze_study_helper_sha256','target_gaze_study_renderer_sha256']:
            job=self.job(True);job[key]='0'*64
            with self.assertRaisesRegex(ValueError,'implementation differs'):
                replay_guide_profiles(ast.parse('def prop_pose():\n pass'),job)

    def test_missing_or_duplicate_pose_boundaries_are_rejected(self):
        for source in ['pass','def prop_pose():\n pass\ndef outer():\n def prop_pose():\n  pass']:
            with self.assertRaisesRegex(ValueError,'exactly one'):
                replay_guide_profiles(ast.parse(source),self.job(True))

if __name__=='__main__':unittest.main()
