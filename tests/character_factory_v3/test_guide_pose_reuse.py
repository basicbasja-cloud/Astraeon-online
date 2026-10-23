import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from certify_guide_pose_reuse import certify


class GuidePoseReuseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.source=Path(self.temp.name)/'a';self.target=Path(self.temp.name)/'b'
        frame={'action':'Recover','source_frame':12,'world_landmarks':{'root':[0.,0.,0.]},'bone_rotations':{'hand':[1.,0.,0.,0.]},'weapon_guide':{'grip':[1.,2.]}}
        self.manifest={'job':{'id':'a','source_sha256':'source','renderer_sha256':'render'},'frame_count':1,'views':{'SE':{'camera':{'ortho':5},'frames':[frame]}}}
        for folder in [self.source,self.target]:
            (folder/'SE').mkdir(parents=True)
            Image.new('RGBA',(8,8),(100,80,60,255)).save(folder/'SE/000.png')
            (folder/'manifest.json').write_text(json.dumps(self.manifest))

    def mutate(self,change):
        target=copy.deepcopy(self.manifest);change(target)
        (self.target/'manifest.json').write_text(json.dumps(target))

    def test_exact_explicit_mapping_certifies_source_only(self):
        result=certify(self.source,self.target,pairs=[(0,0)])
        self.assertEqual(len(result['mappings']),1);self.assertFalse(result['runtime_admitted'])
        self.assertFalse(result['effect_timing_copied'])

    def test_camera_controls_and_nonfinite_coordinates_rejected(self):
        changes=[lambda m:m['views']['SE']['camera'].update(ortho=6),lambda m:m['views']['SE']['frames'][0].update(transition_weight=.5),lambda m:m['views']['SE']['frames'][0]['world_landmarks'].update(root=[float('nan'),0.,0.])]
        for change in changes:
            self.mutate(change)
            with self.assertRaises(ValueError):certify(self.source,self.target,pairs=[(0,0)])

    def test_changed_pixels_rejected(self):
        Image.new('RGBA',(8,8),'red').save(self.target/'SE/000.png')
        with self.assertRaises(ValueError):certify(self.source,self.target,offset=0)

    def test_invalid_mapping_rejected(self):
        for pairs in [[],[(0,1)],[(0,0),(0,0)]]:
            with self.assertRaises(ValueError):certify(self.source,self.target,pairs=pairs)


if __name__=='__main__':unittest.main()
