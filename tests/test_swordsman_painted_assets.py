"""Check actual painted raster exports, not only timeline metadata."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())

class PaintedAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=read('authoring/characters/appearance/swordsman-male-painted/appearance-pack.json')
        cls.motion=read('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json')
        cls.build=read('authoring/characters/builds/swordsman-male/build-manifest.json')
        cls.normalization=read('authoring/characters/builds/swordsman-male/normalization.json')['sequences']
        cls.images={key:Image.open(ROOT/a['file']).copy() for key,a in cls.pack['atlases'].items()}
    def test_atlas_dimensions_hashes_transparency(self):
        for name,atlas in self.pack['atlases'].items():
            path=ROOT/atlas['file'];im=Image.open(path)
            self.assertEqual(im.mode,'RGBA',name)
            self.assertEqual(im.size,(atlas['width'],atlas['height']),name)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),self.build['runtimeAtlases'][name])
            alpha=np.asarray(im.getchannel('A'))
            self.assertGreater((alpha==0).mean(),.1,name)
            self.assertGreater((alpha>(10 if name=='shadow' else 200)).sum(),50,name)
    def test_all_328_body_cells_registered_and_uncropped(self):
        count=0
        for action,directions in self.pack['parts']['body-swordsman']['timelines'].items():
            for direction,sequence in directions.items():
                for i,entry in enumerate(sequence['frames']):
                    ref=entry['layers']['Body'];rect=ref['rect'];atlas=self.pack['atlases'][ref['atlasId']]
                    im=self.images[ref['atlasId']].crop((rect[0],rect[1],rect[0]+rect[2],rect[1]+rect[3]))
                    self.assertEqual(im.size,(320,320));bbox=im.getbbox();self.assertIsNotNone(bbox)
                    self.assertGreater(bbox[0],1);self.assertGreater(bbox[1],1);self.assertLess(bbox[2],319);self.assertLess(bbox[3],319)
                    self.assertLessEqual(abs(bbox[3]-264),3,(action,direction,i,'support registration'))
                    frame=self.motion['actions'][action]['directions'][direction]['frames'][i]
                    self.assertEqual(frame['root'],self.pack['registration']['root'])
                    self.assertTrue(60<frame['anchors']['head']['y']<205,(action,direction,i))
                    count+=1
        self.assertEqual(count,328)
    def test_shared_strip_scale_and_overlapping_recovery(self):
        for key,seq in self.normalization.items():
            if key.startswith('Idle'):continue
            prefix=seq[:10] if key.startswith('BasicAttack') else seq
            self.assertEqual(len({f['scale'] for f in prefix}),1,key)
            if key.startswith('BasicAttack'):
                self.assertEqual(len({f['scale'] for f in seq[10:]}),1,key)
                self.assertTrue(all(f['lockedBoundaryFrames']==[8,9] for f in seq[10:]),key)
    def test_all_directional_body_views_authored_without_mirroring(self):
        self.assertEqual(self.motion['directions'],['S','SW','W','NW','N','NE','E','SE'])
        self.assertEqual(self.pack['mirroring'],'none')
        for action in self.pack['parts']['body-swordsman']['timelines'].values():
            hashes=[]
            for seq in action.values():
                ref=seq['frames'][0]['layers']['Body'];r=ref['rect']
                im=self.images[ref['atlasId']].crop((r[0],r[1],r[0]+r[2],r[1]+r[3]))
                hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
            self.assertEqual(len(set(hashes)),8)
    def test_approved_identity_source_recorded(self):
        source=ROOT/self.pack['source']['reference']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),'750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05')
        self.assertEqual(self.pack['status'],'REQUIRES_OWNER_VISUAL_REVIEW')
        self.assertFalse(self.build['rawROPixelsInProduction'])

if __name__=='__main__':unittest.main()
