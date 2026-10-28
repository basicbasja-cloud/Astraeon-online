import hashlib,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import cutout_asset_store as store

class CutoutStoreIntegrityTests(unittest.TestCase):
 def fixture(self,root):
  image=root/'source.png';pixels=np.zeros((512,512,4),dtype=np.uint8);pixels[100,100]=[20,40,60,255];Image.fromarray(pixels).save(image)
  metadata={'role':'Weapon','canvas':[512,512],'fit_id':'fit','pose_id':'pose','camera_id':'camera','root':[256,422.4],'source_reference':'source'}
  target=root/'store/objects'/f'{hashlib.sha256(pixels.tobytes()).hexdigest()}.png';target.parent.mkdir(parents=True)
  return image,metadata,target
 def test_changed_existing_object_rejected_without_overwrite_or_binding(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);image,metadata,target=self.fixture(root);Image.new('RGBA',(512,512),(5,5,5,255)).save(target);before=target.read_bytes();index={'assets':{},'objects':{}}
   with patch.object(store,'ROOT',root),patch.object(store,'STORE',root/'store'):
    with self.assertRaisesRegex(ValueError,'pixels changed'):store.register(image,metadata,index)
   self.assertEqual(target.read_bytes(),before);self.assertEqual(index,{'assets':{},'objects':{}})
 def test_corrupt_existing_object_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);image,metadata,target=self.fixture(root);target.write_bytes(b'corrupt');index={'assets':{},'objects':{}}
   with patch.object(store,'ROOT',root),patch.object(store,'STORE',root/'store'):
    with self.assertRaisesRegex(ValueError,'unreadable or invalid'):store.register(image,metadata,index)
   self.assertEqual(target.read_bytes(),b'corrupt');self.assertFalse(index['assets'])
 def test_dangling_object_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);image,metadata,target=self.fixture(root);target.symlink_to(root/'missing.png')
   with patch.object(store,'ROOT',root),patch.object(store,'STORE',root/'store'):
    with self.assertRaisesRegex(ValueError,'symlink'):store.register(image,metadata,{'assets':{},'objects':{}})
   self.assertFalse((root/'missing.png').exists())
 def test_existing_valid_object_is_reused(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);image,metadata,target=self.fixture(root);target.write_bytes(image.read_bytes());before=target.read_bytes();index={'assets':{},'objects':{}}
   with patch.object(store,'ROOT',root),patch.object(store,'STORE',root/'store'):key=store.register(image,metadata,index)
   self.assertEqual(target.read_bytes(),before);self.assertIn(key,index['assets'])

if __name__=='__main__':unittest.main()
