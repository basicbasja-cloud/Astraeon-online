"""Actual Blender regression for the isolated cast gaze adaptation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools/character_factory_v3'
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
SOURCE=ROOT/'authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

@unittest.skipUnless(shutil.which('blender')and SOURCE.exists(),'Blender and retained Mesh2Motion source required')
class TargetGazeGuideStudyTests(unittest.TestCase):
    def test_actual_cast_changes_head_rotation_without_changing_body_or_grip(self):
        job=json.loads((BASE/'research/tall-guide-proportion-pilot-20261027/mage130-job.json').read_text())
        reference=json.loads((BASE/'research/tall-guide-proportion-pilot-20261027/mage130-capture/manifest.json').read_text())
        target=reference['views']['SW']['frames'][0]['bone_rotations']['head']
        job.update({'id':'target-gaze-regression','frames':3,'directions':['SW'],'resolution':256,
                    'target_gaze_study':{'reference_head_world_quaternion':target,'maximum_correction_degrees':50},
                    'target_gaze_study_renderer_sha256':sha(TOOLS/'render_target_gaze_guide_study.py'),
                    'target_gaze_study_helper_sha256':sha(TOOLS/'target_gaze_guide_study.py')})
        original=sha(SOURCE)
        with tempfile.TemporaryDirectory()as directory:
            folder=Path(directory);path=folder/'job.json';path.write_text(json.dumps(job));output=folder/'capture'
            command=['blender','-b','-t','2','--python-exit-code','1','--python',str(TOOLS/'render_target_gaze_guide_study.py'),'--','--job',str(path),'--output',str(output)]
            with(folder/'blender.log').open('w')as log:
                result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180)
            self.assertEqual(result.returncode,0,(folder/'blender.log').read_text()[-2400:])
            proof=json.loads((output/'target-gaze-proof.json').read_text())
            manifest=json.loads((output/'manifest.json').read_text())
            rows=proof['applications']
            self.assertGreater(max(r['correction_degrees']for r in rows),10,'Exercise an actual turning torso, not just the reference pose')
            self.assertTrue(all(r['maximum_protected_body_matrix_error']<=2e-6 for r in rows))
            self.assertTrue(all(r['head_position_error_m']<=2e-6 for r in rows))
            self.assertTrue(all(r['protected_bone_count']==64 for r in rows))
            for frame in manifest['views']['SW']['frames']:
                q=np.asarray(frame['bone_rotations']['head']);q/=np.linalg.norm(q)
                self.assertLess(min(np.linalg.norm(q-target),np.linalg.norm(q+target)),3e-6)
            rendered=manifest['render_pose_freeze']['rendered_frames'];self.assertEqual(len(rendered),3)
            self.assertTrue(all(actor['bones']==66 and actor['max_world_matrix_component_error']<=1e-5 for frame in rendered for actor in frame['actors']))
            self.assertEqual(len(manifest['staff_grip_adaptation']['rendered_grip_checks']),3)
            self.assertFalse(proof['runtime_admitted'])
        self.assertEqual(sha(SOURCE),original)

if __name__=='__main__':unittest.main()
