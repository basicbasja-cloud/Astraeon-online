import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from apply_manual_head_polygons import apply
from replay_cutout_labels import replay
import replay_cutout_labels as replayer
from track_visible_cutouts import sha


class ManualCutoutReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.masters=self.root/'masters';self.masters.mkdir();self.previous=self.root/'previous';(self.previous/'Weapon').mkdir(parents=True)
        a=np.zeros((768,768,4),np.uint8);a[20:35,20:35]=[170,120,80,255];a[50:80,20:35]=[80,100,40,255];a[40:44,40:60]=[180,180,200,180]
        Image.fromarray(a).save(self.masters/'000.png');w=np.zeros_like(a);w[40:44,40:60]=a[40:44,40:60];Image.fromarray(w).save(self.previous/'Weapon/000.png')
        self.annotations=self.root/'annotations.json';self.annotations.write_text(json.dumps({'canvas':[768,768],'frames':[{'index':0,'master_sha256':sha(self.masters/'000.png'),'crop_origin':[0,0],'polygon':[[19,19],[36,19],[36,36],[19,36]]}]}))

    def test_labels_rebuild_exact_pngs_without_segmentation_model(self):
        source=self.root/'source';apply(self.masters,self.previous,self.annotations,source)
        result=replay(source/'receipt.json',self.masters,self.root/'rebuilt')
        self.assertEqual(len(result['role_checks']),3);self.assertFalse(result['requires_sam2'])
        self.assertFalse(result['visual_approval_implied'])

    def test_changed_weapon_colors_cannot_be_used_as_same_frame_subset(self):
        path=self.previous/'Weapon/000.png';a=np.array(Image.open(path));a[40,40]=[255,0,0,255];Image.fromarray(a).save(path)
        with self.assertRaisesRegex(ValueError,'same-frame'):apply(self.masters,self.previous,self.annotations,self.root/'rejected')

    def test_replay_rejects_changed_labels(self):
        source=self.root/'source';apply(self.masters,self.previous,self.annotations,source)
        Image.new('L',(768,768)).save(source/'labels/000.png')
        with self.assertRaisesRegex(ValueError,'changed'):replay(source/'receipt.json',self.masters,self.root/'rejected')

    def test_hand_occlusion_is_a_separate_exact_visible_role(self):
        data=json.loads(self.annotations.read_text());data['frames'][0]['hand_occluder']=[[[41,39],[48,39],[48,45],[41,45]]]
        self.annotations.write_text(json.dumps(data));source=self.root/'source';apply(self.masters,self.previous,self.annotations,source)
        self.assertIsNotNone(Image.open(source/'WeaponHandOccluder/000.png').getbbox())
        self.assertIn(6,np.unique(np.array(Image.open(source/'labels/000.png'))))
        result=replay(source/'receipt.json',self.masters,self.root/'rebuilt');self.assertEqual(len(result['role_checks']),4)

    def test_other_png_compression_preserves_exact_pixel_replay(self):
        source=self.root/'source';apply(self.masters,self.previous,self.annotations,source);original_import=replayer.import_frame
        def reencode(master,labels,targets):
            original_import(master,labels,targets)
            for target in targets.values():
                with Image.open(target)as image:copy=image.copy()
                copy.save(target,compress_level=0)
        with patch.object(replayer,'import_frame',reencode):result=replay(source/'receipt.json',self.masters,self.root/'rebuilt')
        self.assertTrue(all(r['matches_frozen_export']for r in result['role_checks']));self.assertTrue(any(not r['png_bytes_identical']for r in result['role_checks']))


if __name__=='__main__':unittest.main()
