from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys,hashlib,shutil
from scipy import ndimage
sys.path.insert(0,'tools/character_factory_v3')
from register_planted_foot_masters import observed_sole,rigid_translation
from source_segment_timing import source_timing
b=Path('authoring/characters/factory-v3/patch-0.0.1');src=b/'review/mage-female-sw-full-correction-20261027/Master';old=b/'review/mage-female-sw-canonical-pilot-20261027/Master';o=b/'review/mage-female-sw-shared-fit-registration-20261027';(o/'Master').mkdir(parents=True,exist_ok=True);manifest=json.loads((b/'guides/fcfd5fa441325973a7db/manifest.json').read_text());rows=manifest['views']['SW']['frames'];a=np.array(Image.open(src/'000.png'));r,g,z=a[:,:,:3].astype(float).transpose((2,0,1));yy,xx=np.indices(a.shape[:2]);hair=(a[:,:,3]>200)&(xx>320)&(xx<430)&(yy>280)&(yy<390)&(r>g*1.35)&(g>z*1.1)&((r-g)>1.8*(g-z));labels,n=ndimage.label(hair);sizes=np.bincount(labels.ravel());sizes[0]=0;crown=float(np.where(labels==sizes.argmax())[0].min());ground=float(np.where(a[:,:,3]>200)[0].max());scale=(554-328)/(ground-crown);first_sole=sorted(observed_sole(Image.open(src/'000.png'))[1],key=lambda x:x['point'][0]);oldsole=sorted(observed_sole(Image.open(old/'000.png'))[1],key=lambda x:x['point'][0]);tx=np.array([v['point']for v in oldsole])[:,0].mean()-scale*np.array([v['point']for v in first_sole])[:,0].mean();ty=554-scale*ground;proof=[];previews=[];first=None;g0=np.array([rows[0]['landmarks'][k]for k in ['foot_r','foot_l']])
for i in range(24):
 p=src/f'{i:03d}.png';im=Image.open(p).convert('RGBA').transform((768,768),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC);pts=np.array([r['point']for r in sorted(observed_sole(im)[1],key=lambda x:x['point'][0])]);
 if len(pts)!=2:raise ValueError('Ambiguous visible sole association')
 if first is None:first=pts.copy()
 expected=first+(np.array([rows[i]['landmarks'][k]for k in ['foot_r','foot_l']])-g0)*.5;delta=np.rint((expected-pts).mean(axis=0)).astype(int);im=rigid_translation(im,delta);im.save(o/'Master'/f'{i:03d}.png');residual=np.linalg.norm(pts+delta-expected,axis=1)*.3125;proof.append({'index':i,'whole_frame_integer_translation':delta.tolist(),'sole_residual_runtime_px':residual.tolist(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((o/'Master'/f'{i:03d}.png').read_bytes()).hexdigest()});bg=Image.new('RGBA',(384,384),'#ddd');bg.alpha_composite(im.crop((192,256,576,640)));v=bg.convert('RGB');ImageDraw.Draw(v).text((5,5),f'Registered whole master {i:02d} | DRAFT',fill='black');previews.append(v)
timing=source_timing(manifest,'SW')
for name,factor in [('source-time',1),('slow',3)]:previews[0].save(o/f'{name}.gif',save_all=True,append_images=previews[1:],duration=[d*factor for d in timing['gif_durations_ms']],loop=0,disposal=2)
a=Image.new('RGB',(2304,1536),'#ddd')
for i,v in enumerate(previews):a.paste(v,((i%6)*384,(i//6)*384))
a.save(o/'contact.jpg',quality=98);(o/'receipt.json').write_text(json.dumps({'status':'SHARED_BASELINE_FIT_WHOLE_FRAME_REGISTRATION_REVIEW','shared_scale':scale,'shared_translation':[tx,ty],'per_frame_scale':False,'limb_warping':False,'source_timing':timing,'frames':proof,'maximum_two_sole_residual_runtime_px':max(max(r['sole_residual_runtime_px'])for r in proof),'anatomy_approved':False,'runtime_admitted':False},indent=2)+'\n');shutil.copy2(__file__,o/'registration-source.py');print(scale,tx,ty,'max residual',max(max(r['sole_residual_runtime_px'])for r in proof))
