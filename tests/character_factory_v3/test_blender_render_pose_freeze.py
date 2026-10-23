"""Actual Blender render regression; synthetic parts are not used as artwork."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools/character_factory_v3';sys.path.insert(0,str(TOOLS))
import render_frozen_patch001_guides as frozen


@unittest.skipUnless(shutil.which('blender')and(ROOT/'authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb').exists(),'Blender and retained source GLB required')
class ActualRenderPoseFreezeTests(unittest.TestCase):
    def test_adapted_staff_hand_is_visible_at_the_recorded_wrist(self):
        base=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
        ledger=json.loads((base/'ledger.json').read_text())
        original=ledger['guide_jobs'][ledger['action_guide_bindings']['Mage/CastRelease']]
        with tempfile.TemporaryDirectory()as directory:
            folder=Path(directory);job={**original,'id':'render-freeze-regression','directions':['SE'],'resolution':512,'frames':1,
                                        'render_pose_freeze_revision':1,'render_pose_freeze_sha256':frozen.sha(frozen.__file__)}
            path=folder/'job.json';path.write_text(json.dumps(job));manifests={};pixels={}
            for mode,script in [('baseline','render_patch001_guides.py'),('fixed','render_frozen_patch001_guides.py')]:
                output=folder/mode
                command=['blender','-b','-t','2','--python-exit-code','1','--python',str(TOOLS/script),'--','--job',str(path),'--output',str(output),'--static']
                with(folder/(mode+'.log')).open('w')as log:
                    result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180)
                self.assertEqual(result.returncode,0,(folder/(mode+'.log')).read_text()[-1800:])
                manifests[mode]=json.loads((output/'manifest.json').read_text());pixels[mode]=np.array(Image.open(output/'SE/000.png').convert('RGBA'))
            before=manifests['baseline']['views']['SE'];after=manifests['fixed']['views']['SE']
            self.assertEqual(before['camera'],after['camera'])
            for name,value in before['frames'][0]['world_landmarks'].items():
                np.testing.assert_allclose(value,after['frames'][0]['world_landmarks'][name],atol=1e-6)
            x,y=map(round,after['frames'][0]['landmarks']['hand_r']);mask=pixels['fixed'][max(0,y-1):y+2,max(0,x-1):x+2,3]
            self.assertGreater(int(mask.max()),0,'Rendered body must include the intended adapted right wrist, not just correct bone metadata')
            proof=manifests['fixed']['render_pose_freeze'];self.assertEqual(len(proof['rendered_frames']),1)
            self.assertTrue(all(actor['max_world_matrix_component_error']<=1e-5 for actor in proof['rendered_frames'][0]['actors']))
            print('ACTUAL_RENDER_FREEZE '+json.dumps({'status':'PASS','resolution':512,'right_wrist':[x,y],
                  'baseline_wrist_alpha':int(pixels['baseline'][y,x,3]),'fixed_wrist_alpha':int(pixels['fixed'][y,x,3]),
                  'camera_and_source_landmarks_unchanged':True}))


if __name__=='__main__':unittest.main()
