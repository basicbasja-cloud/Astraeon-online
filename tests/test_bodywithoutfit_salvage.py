import hashlib,json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
class SalvageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads((R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text());cls.receipt=json.loads((R/'authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json').read_text());cls.ims={k:Image.open(R/v['file']).convert('RGBA') for k,v in cls.p['atlases'].items()};cls.old={k:Image.open(R/'assets/characters/swordsman-ro1-painted-v1'/f'{k}.png').convert('RGBA') for k in ['body-idle','body-walk','body-basicattack']}
 def test_328_exact_body_and_head_reassemblies_preserve_all_face_and_costume_pixels(self):
  for f in self.receipt['frames']:
   a,d,i=f['action'],f['direction'],f['frame'];j=self.p['bodyContract']['directions'].index(d)
   body=self.ims['body-'+a.lower()].crop((i*320,j*320,(i+1)*320,(j+1)*320));headref=self.p['parts']['swordsman-head']['timelines'][a][d]['frames'][i]['layers']['HeadBase'];rect=headref['rect'];head=self.ims[rect and headref['atlasId']].crop((rect[0],rect[1],rect[0]+96,rect[1]+96));off=headref['trim']['offset'];body.alpha_composite(head,tuple(off));old=self.old['body-'+a.lower()].crop((i*320,j*320,(i+1)*320,(j+1)*320));self.assertTrue(np.array_equal(np.asarray(body),np.asarray(old)),(a,d,i));self.assertEqual(hashlib.sha256(body.tobytes()).hexdigest(),f['sourceRGBA'])
  self.assertEqual(len(self.receipt['frames']),328)
 def test_atlas_receipts_and_real_transparent_pixels(self):
  for id,a in self.p['atlases'].items():
   im=self.ims[id];self.assertEqual(im.size,(a['width'],a['height']));self.assertEqual(hashlib.sha256((R/a['file']).read_bytes()).hexdigest(),self.receipt['runtimeAtlases'][id]);self.assertGreater((np.asarray(im)[:,:,3]==0).mean(),.1)
 def test_proof_costume_has_distinct_complete_body_pixels_and_no_head(self):
  for a in ['idle','walk','basicattack']:
   default=np.asarray(self.ims['body-'+a]);royal=np.asarray(self.ims['royal-'+a]);self.assertTrue(np.array_equal(default[:,:,3],royal[:,:,3]));self.assertGreater(np.count_nonzero(default!=royal),1000)
 def test_authored_attack_grips_are_on_actual_opaque_actor_pixels(self):
  for d,seq in self.p['bodyContract']['anchorRegistration']['BasicAttack'].items():
   j=self.p['bodyContract']['directions'].index(d);points=json.loads((R/'authoring/characters/builds/swordsman-registration-v1/socket-overrides.json').read_text())['BasicAttack/'+d]
   for i in range(16):
    x,y=points[str(i)]['mainHand'];im=self.old['body-basicattack'];self.assertGreater(im.getpixel((i*320+x,j*320+y))[3],200,(d,i,x,y))
