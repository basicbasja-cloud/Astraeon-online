from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy import ndimage
b=Path('authoring/characters/factory-v3/patch-0.0.1');src=b/'review/mage-female-head-filter-support-v5-20261027';out=b/'review/mage-female-head-fringe-ownership-v7-20261027';out.mkdir(exist_ok=True);receipt=json.loads((src/'receipt.json').read_text());seg=json.loads((b/'review/mage-female-target-gaze-sequence-heads-v3-20261027/receipt.json').read_text());fit=json.loads((b/'review/mage-female-single-frame-trace-20261027/receipt.json').read_text());recipe=json.loads((b/'painted-candidates/mage-female-single-frame-trace-20261027/sequence-reference-recipe.json').read_text());rows=[]
for i in range(24):
 head=np.array(Image.open(src/'HeadHair'/f'{i:03d}.png'));rest=np.array(Image.open(src/'BodyRest'/f'{i:03d}.png'));master=np.array(Image.open(b/'review/mage-female-single-frame-trace-20261027/Master'/f'{i:03d}.png'));r=next(r for r in seg['frames']if r['index']==i);row=next(r for r in fit['frames']if r['index']==i);vp=recipe['canonical_viewport768']if i in recipe['indices']else[224,224,576,576];raw=Image.open(b/'painted-candidates/mage-female-single-frame-trace-20261027'/f'raw{i:03d}.png');s=(vp[2]-vp[0])/raw.width*fit['shared_scale'];offset=np.array(vp[:2])*fit['shared_scale']+fit['shared_translation']+np.array(row['whole_frame_integer_translation']);face=np.array(r['positive'][-1])*s+offset;shaft=r['observed_jewel_center_raw'][0]*s+offset[0];bbox=Image.fromarray(head).getbbox();labels,n=ndimage.label(rest[:,:,3]>0,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0;main=int(sizes.argmax());returned=[]
 for k in range(1,n+1):
  if k==main or sizes[k]>100:continue
  y,x=np.where(labels==k)
  if x.min()<bbox[0]-4 or x.max()>bbox[2]+4 or y.min()<bbox[1]-4 or y.max()>min(bbox[3]+4,face[1]+5) or np.any(abs(x-shaft)<3):continue
  mask=labels==k;head[mask]=master[mask];rest[mask]=0;returned.append({'pixels':int(sizes[k]),'bbox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]})
 # Above the observed face, this bounded region contains head/hair and the staff only.
 yy,xx=np.indices((768,768));upper=(xx>=bbox[0]-4)&(xx<bbox[2]+4)&(yy>=bbox[1]-4)&(yy<face[1]-5)&(abs(xx-shaft)>3)&(rest[:,:,3]>0);head[upper]=master[upper];rest[upper]=0
 for role,a in [('HeadHair',head),('BodyRest',rest)]:
  (out/role).mkdir(exist_ok=True);Image.fromarray(a).save(out/role/f'{i:03d}.png')
 re=Image.new('RGBA',(768,768));re.alpha_composite(Image.fromarray(rest));re.alpha_composite(Image.fromarray(head));visible=master[:,:,3]>0;assert np.array_equal(np.array(re)[visible],master[visible]);assert np.array_equal(np.array(re)[:,:,3],master[:,:,3]);rows.append({'index':i,'detached_head_region_components':returned,'native_head_only_region_pixels_returned':int(upper.sum()),'head_only_region_limit_author768':{'bbox':list(bbox),'maximum_y':float(face[1]-5),'protected_staff_x':float(shaft),'staff_halfwidth':3},'visible_recomposition_mismatch_pixels':0,'semantic_approved':False})
(out/'receipt.json').write_text(json.dumps({'status':'DETACHED_NATIVE_HEAD_FRINGE_OWNERSHIP_STUDY','frames':rows,'master_pixels_modified':False,'also_returns_native_head_only_region_above_observed_face':True,'staff_corridor_and_largest_body_component_protected':True,'BodyRest_contains_weapon':True,'runtime_admitted':False},indent=2)+'\n');(out/'repair-source.py').write_bytes(Path(__file__).read_bytes())
