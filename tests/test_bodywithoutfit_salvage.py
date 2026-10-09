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
   body=self.ims['body-'+a.lower()].crop((i*320,j*320,(i+1)*320,(j+1)*320));headref=self.p['parts']['swordsman-head']['timelines'][a][d]['frames'][i]['layers']['HeadBase'];rect=headref['rect'];head=self.ims[rect and headref['atlasId']].crop((rect[0],rect[1],rect[0]+96,rect[1]+96));off=headref['trim']['offset'];body.alpha_composite(head,tuple(off));sx,sy,sw,sh=f['sourceRect'];old=self.old['body-'+a.lower()].crop((sx,sy,sx+sw,sy+sh));self.assertTrue(np.array_equal(np.asarray(body),np.asarray(old)),(a,d,i));self.assertEqual(hashlib.sha256(body.tobytes()).hexdigest(),f['sourceRGBA'])
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
    x,y=points[str(i)]['mainHand'];im=self.ims['body-basicattack'];self.assertGreater(im.getpixel((i*320+x,j*320+y))[3],200,(d,i,x,y))
 def test_costume_colour_proof_keeps_entire_head_neck_seam_pixel_identical(self):
  for f in self.receipt['frames']:
   a,d,i=f['action'],f['direction'],f['frame'];j=self.p['bodyContract']['directions'].index(d);l,t,r,b=f['headRect'];rect=(i*320+l,j*320+t,i*320+r,j*320+b)
   self.assertTrue(np.array_equal(np.asarray(self.ims['body-'+a.lower()].crop(rect)),np.asarray(self.ims['royal-'+a.lower()].crop(rect))),(a,d,i))
 def test_bounded_contact_and_held_fist_repairs_reuse_existing_painted_poses_without_generation(self):
  repaired=[f for f in self.receipt['frames'] if f.get('poseRepair')]
  self.assertEqual([(f['action'],f['direction'],f['frame'],f['sourceFrame']) for f in repaired],[('BasicAttack','SW',7,8),('BasicAttack','W',10,11),('BasicAttack','W',14,13),('BasicAttack','W',15,13),('BasicAttack','NW',7,8)])
  # Split masks can differ where the target grip occludes the ear. The whole
  # Body + independent Head must still exactly equal the retained source.
  for f in repaired:
   j=self.p['bodyContract']['directions'].index(f['direction']);i=f['frame'];body=self.ims['body-basicattack'].crop((i*320,j*320,(i+1)*320,(j+1)*320));ref=self.p['parts']['swordsman-head']['timelines']['BasicAttack'][f['direction']]['frames'][i]['layers']['HeadBase'];x,y,w,h=ref['rect'];body.alpha_composite(self.ims[ref['atlasId']].crop((x,y,x+w,y+h)),tuple(ref['trim']['offset']));source=f['sourceFrame'];self.assertTrue(np.array_equal(np.asarray(body),np.asarray(self.old['body-basicattack'].crop((source*320,j*320,(source+1)*320,(j+1)*320)))))
