import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import render_hit_snapshot_guides as capture
from validate_render_snapshot_capture import valid_render_snapshot_capture
import patch001_factory as factory


class HitSnapshotCaptureTests(unittest.TestCase):
    def geometry(self):
        return {'source_actions':['Hit_Chest'],'renderer_sha256':capture.sha(capture.HERE/'render_patch001_guides.py')}

    def test_profile_is_explicit_and_source_specific(self):
        job=capture.planned_geometry(self.geometry(),'native-hit-declared-pose-v1')
        capture.validate_job(job)
        for changes in ({'source_actions':['Walk']},{'render_snapshot_revision':True},
                        {'render_snapshot_sha256':'old'},{'render_snapshot_png_sha256':'old'},
                        {'retarget_to':'other.glb'},{'staff_arm_reference':'Idle_Lantern'},
                        {'entry_transition':{'action':'Idle_Sword'}}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                capture.validate_job({**job,**changes})
        with self.assertRaises(ValueError):capture.planned_geometry(self.geometry(),'unknown-profile')

    def test_instrumentation_wraps_one_render_call_without_muting_curves(self):
        tree=capture.instrument((capture.HERE/'render_patch001_guides.py').read_text())
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)]
        guarded=[n for n in calls if isinstance(n.func,ast.Name)and n.func.id=='_snapshot_render']
        self.assertEqual(len(guarded),1)
        self.assertEqual([ast.unparse(n)for n in guarded[0].args[:4]],['rig','i','rec','bpy.ops.render.render'])
        self.assertFalse(any(isinstance(n.func,ast.Attribute)and ast.unparse(n.func)=='bpy.ops.render.render'for n in calls))
        with self.assertRaisesRegex(ValueError,'one canonical render boundary'):
            capture.instrument('bpy.ops.render.render()\nbpy.ops.render.render()')

    def test_matrix_check_rejects_nonfinite_data(self):
        matrix=[[float(r==c)for c in range(4)]for r in range(4)];changed=copy.deepcopy(matrix)
        changed[2][3]=.575876
        self.assertAlmostEqual(capture.matrix_error(matrix,changed),.575876)
        changed[2][3]=float('nan')
        with self.assertRaises(ValueError):capture.matrix_error(matrix,changed)

    def test_curve_fingerprint_detects_handle_keys_and_mute_changes(self):
        point=SimpleNamespace(co=[0.,1.],handle_left=[-1.,1.],handle_right=[1.,1.],interpolation='BEZIER')
        curve=SimpleNamespace(data_path='location',array_index=0,mute=False,keyframe_points=[point])
        action=SimpleNamespace(name='Hit_Chest',fcurves=[curve]);original=capture.action_fingerprint([action])
        point.handle_right[1]=2.;self.assertNotEqual(capture.action_fingerprint([action]),original)
        point.handle_right[1]=1.;curve.mute=True;self.assertNotEqual(capture.action_fingerprint([action]),original)
        curve.mute=False;point.co[1]=3.;self.assertNotEqual(capture.action_fingerprint([action]),original)


class HitSnapshotCacheTests(unittest.TestCase):
    def fixture(self,folder):
        (folder/'SW').mkdir(parents=True);path=folder/'SW/000.png'
        Image.new('RGBA',(8,8),(80,90,100,255)).save(path)
        implementation=capture.sha(capture.__file__);png=capture.sha(capture.HERE/'seal_source_guide_replay.py')
        job={'id':'snapshot-test','frames':1,'directions':['SW'],'resolution':8,'render_snapshot_revision':1,
             'render_snapshot_sha256':implementation,'render_snapshot_png_sha256':png}
        matrix=[[float(r==c)for c in range(4)]for r in range(4)]
        row={'image':'SW/000.png','index':0,'source_action':'Hit_Chest','source_frame':5.,'bones':66,
             'declared_object_world_matrix':matrix,'evaluated_object_world_matrix_after_render':copy.deepcopy(matrix),
             'max_before_render_matrix_component_error':0.,'max_after_render_matrix_component_error':0.,
             'joints':{name:{'declared_source_px':[4.,5.],'evaluated_after_render_px':[4.,5.],
                             'distance_runtime_px':0.}for name in('head','pelvis','hand_r','hand_l','foot_r','foot_l')},
             'canvas':[8,8],'png_sha256':capture.sha(path),'rgba_sha256':'a'*64}
        manifest={'job':job,'frame_count':1,'views':{'SW':{'frames':[{'action':'Hit_Chest','source_frame':5.}]}},
            'implementation_digests_at_process_start':{'render_hit_snapshot_guides.py':implementation,'seal_source_guide_replay.py':png},
            'render_snapshot':{'revision':1,'applied':True,'implementation_sha256':implementation,
                'source_fcurves_or_mute_flags_changed':False,'source_samples_or_camera_changed':False,
                'source_fcurves_sha256_before_and_after':'b'*64,'frames':[row]}}
        return job,manifest

    def test_complete_evidence_counts_only_as_source_capture(self):
        with tempfile.TemporaryDirectory()as temporary:
            folder=Path(temporary);job,manifest=self.fixture(folder)
            self.assertTrue(valid_render_snapshot_capture(job,manifest,folder))
            (folder/'manifest.json').write_text(json.dumps(manifest))
            self.assertTrue(factory.receipt_valid(job,folder))

    def test_observation_or_bad_pose_evidence_never_counts_as_valid_cache(self):
        with tempfile.TemporaryDirectory()as temporary:
            folder=Path(temporary);job,original=self.fixture(folder)
            mutations=[lambda p:p.update(applied=False),lambda p:p.update(revision=True),
                       lambda p:p.update(source_fcurves_or_mute_flags_changed=True),
                       lambda p:p['frames'][0].update(max_after_render_matrix_component_error=float('nan')),
                       lambda p:p['frames'][0].update(max_after_render_matrix_component_error=.01),
                       lambda p:p['frames'][0].update(index=True),
                       lambda p:p['frames'][0]['evaluated_object_world_matrix_after_render'][2].__setitem__(3,.5),
                       lambda p:p.update(frames=[])]
            for mutate in mutations:
                manifest=copy.deepcopy(original);mutate(manifest['render_snapshot'])
                self.assertFalse(valid_render_snapshot_capture(job,manifest,folder))
            bad=copy.deepcopy(original);bad['render_snapshot']['frames'][0]['joints']['hand_r']['evaluated_after_render_px']=[6.,5.]
            self.assertFalse(valid_render_snapshot_capture(job,bad,folder))

    def test_altered_png_and_incomplete_direction_coverage_are_rejected(self):
        with tempfile.TemporaryDirectory()as temporary:
            folder=Path(temporary);job,manifest=self.fixture(folder)
            self.assertFalse(valid_render_snapshot_capture({**job,'directions':['SW','NE']},manifest,folder))
            Image.new('RGBA',(8,8),'red').save(folder/'SW/000.png')
            self.assertFalse(valid_render_snapshot_capture(job,manifest,folder))
            self.assertFalse(valid_render_snapshot_capture({**job,'resolution':0},manifest,folder))


class SnapshotRenderRoutingTests(unittest.TestCase):
    def test_renderer_receives_a_fresh_directory_and_log_is_kept(self):
        with tempfile.TemporaryDirectory()as temporary:
            base=Path(temporary);job={'id':'test','render_snapshot_revision':1};folder=base/'guides/test'
            calls=[]
            def render(command,**kwargs):
                self.assertFalse(folder.exists());self.assertEqual(command[command.index('--output')+1],str(folder))
                folder.mkdir();calls.append(command)
                return SimpleNamespace(returncode=0)
            with patch.object(factory,'BASE',base),patch.object(factory,'receipt_valid',side_effect=[False,True]),\
                 patch.object(capture,'validate_job'),patch.object(factory.subprocess,'run',side_effect=render):
                self.assertEqual(factory.render_one(job)['state'],'SOURCE_GUIDE_CAPTURED')
            self.assertEqual(len(calls),1);self.assertTrue((folder/'render.log').is_file())

    def test_partial_capture_is_preserved_without_launching_a_renderer(self):
        with tempfile.TemporaryDirectory()as temporary:
            base=Path(temporary);folder=base/'guides/test';folder.mkdir(parents=True)
            (folder/'prior.txt').write_text('keep')
            with patch.object(factory,'BASE',base),patch.object(factory,'receipt_valid',return_value=False),\
                 patch.object(capture,'validate_job'),patch.object(factory.subprocess,'run')as run:
                with self.assertRaisesRegex(RuntimeError,'Preserve the incomplete'):factory.render_one({'id':'test','render_snapshot_revision':1})
                run.assert_not_called()
            self.assertEqual((folder/'prior.txt').read_text(),'keep')


if __name__=='__main__':unittest.main()
