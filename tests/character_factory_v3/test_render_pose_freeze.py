import sys
import tempfile
import unittest
import json
from unittest.mock import patch
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
import render_frozen_patch001_guides as frozen
import patch001_factory as factory


class RenderPoseFreezeTests(unittest.TestCase):
    def test_explicit_revision_and_current_implementation_are_required(self):
        frozen.validate_job({'render_pose_freeze_revision':1,'render_pose_freeze_sha256':frozen.sha(frozen.__file__)})
        for job in [{},{'render_pose_freeze_revision':True},{'render_pose_freeze_revision':1,'render_pose_freeze_sha256':'stale'}]:
            with self.assertRaises(ValueError):frozen.validate_job(job)

    def test_png_packaging_preserves_every_visible_rgb_and_alpha(self):
        with tempfile.TemporaryDirectory()as directory:
            path=Path(directory)/'source.png';a=np.zeros((16,16,4),dtype=np.uint8)
            a[:,:,:3]=[91,73,68];a[4:8,4:8]=[250,245,240,150];a[10,12]=[200,100,50,255]
            Image.fromarray(a).save(path);record=frozen.compact_capture(path);result=np.array(Image.open(path))
            np.testing.assert_array_equal(result[:,:,3],a[:,:,3]);np.testing.assert_array_equal(result[a[:,:,3]>0],a[a[:,:,3]>0])
            self.assertTrue(np.all(result[a[:,:,3]==0]==0));self.assertFalse(record['visible_rgb_or_alpha_changed'])

    def test_cache_rejects_missing_pose_proof_or_changed_render_pixels(self):
        with tempfile.TemporaryDirectory()as directory:
            base=Path(directory);folder=base/'guides/test';(folder/'SE').mkdir(parents=True)
            image=folder/'SE/000.png';Image.new('RGBA',(8,8),(50,30,10,255)).save(image)
            implementation=frozen.sha(frozen.__file__)
            job={'id':'test','frames':1,'directions':['SE'],'resolution':8,'render_pose_freeze_revision':1,'render_pose_freeze_sha256':implementation}
            manifest={'job':job,'frame_count':1,'views':{'SE':{'frames':[{}]}},'implementation_digests_at_process_start':{'render_frozen_patch001_guides.py':implementation}}
            path=folder/'manifest.json'
            with patch.object(factory,'BASE',base):
                path.write_text(json.dumps(manifest));self.assertFalse(factory.receipt_valid(job))
                manifest['render_pose_freeze']={'revision':1,'implementation_sha256':implementation,'rendered_frames':[{'image':'SE/000.png','actors':[{'max_world_matrix_component_error':0.}]}]}
                manifest['png_normalization']={'frames':[{'image':'SE/000.png','normalized_sha256':frozen.sha(image),'visible_rgb_or_alpha_changed':False}]}
                path.write_text(json.dumps(manifest));self.assertTrue(factory.receipt_valid(job))
                Image.new('RGBA',(8,8),'red').save(image);self.assertFalse(factory.receipt_valid(job))

    def test_cache_rejects_nonfinite_pose_measurements(self):
        # Contract check is covered with a complete generated fixture above;
        # a nonfinite/error-bearing actor must never count as a frozen pose.
        with tempfile.TemporaryDirectory()as directory:
            base=Path(directory);folder=base/'guides/test';(folder/'SE').mkdir(parents=True)
            image=folder/'SE/000.png';Image.new('RGBA',(8,8)).save(image);implementation=frozen.sha(frozen.__file__)
            job={'id':'test','frames':1,'directions':['SE'],'resolution':8,'render_pose_freeze_revision':1,'render_pose_freeze_sha256':implementation}
            manifest={'job':job,'frame_count':1,'views':{'SE':{'frames':[{}]}},'implementation_digests_at_process_start':{'render_frozen_patch001_guides.py':implementation},'render_pose_freeze':{'revision':1,'implementation_sha256':implementation,'rendered_frames':[{'image':'SE/000.png','actors':[{'max_world_matrix_component_error':float('nan')}]}]},'png_normalization':{'frames':[{'image':'SE/000.png','normalized_sha256':frozen.sha(image),'visible_rgb_or_alpha_changed':False}]}}
            (folder/'manifest.json').write_text(json.dumps(manifest))
            with patch.object(factory,'BASE',base):self.assertFalse(factory.receipt_valid(job))


if __name__=='__main__':unittest.main()
