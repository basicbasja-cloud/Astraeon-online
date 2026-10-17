from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
import numpy as np,json,hashlib,importlib.util
root=Path.cwd();g=root/'work/all-actions-v61/generation';out=g/'W-candidate2';out.mkdir(exist_ok=True)
raw=Image.open('/workspace/generated_images/exec-86d2b3b2-82e2-47f1-8057-44254cdf6232.png').convert('RGBA');assert raw.size==(1536,1024)
mapping=list(range(8));notes=[];small=[]
for i,slot in enumerate(mapping):
 x=i%4*384;y=i//4*512;im=raw.crop((x,y,x+384,y+512));kind='native_whole_pose';rect=[32,70,365,504]
 a=np.array(im);keep=np.zeros(a.shape[:2],bool);keep[rect[1]:rect[3],rect[0]:rect[2]]=True
 # Cyan side tick is a documented guide in blank lower-right panel margin.
 keep[473:482,282:384]=False;keep[473:482,0:104]=False
 core=(a[:,:,3]>=128)&keep;components,n=label(core);areas=np.bincount(components.ravel());areas[0]=0;owner=int(np.argmax(areas));other=[int(v)for j,v in enumerate(areas)if j and j!=owner and v>=40];assert not other,('detached opaque art or foreign guide',i,other)
 support=binary_dilation(components==owner,iterations=3)&keep
 b=a.copy();b[~support]=0;assert np.array_equal(b[support],a[support]);image=Image.fromarray(b);(out/'native-keys').mkdir(exist_ok=True);image.save(out/'native-keys'/f'{i:02}.png');small.append(image)
 ys,xs=np.where(b[:,:,3]>=128);notes.append({'key':i,'source_selection':slot,'source_kind':kind,'fixed_source_annotation_rect':rect,'foreground_core_area':int(areas[owner]),'other_opaque_components_ge40':other,'matte_support':'one opaque primary figure plus3px edge envelope; sourceRGBA byte exact inside; reject other large islands, no deleted body parts','native_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'native_sha256':hashlib.sha256((out/'native-keys'/f'{i:02}.png').read_bytes()).hexdigest()})
# One neutral-only bank calibration, applied to every key. Source rect/pixel
# geometry, not a fitted pose/foot normalization. Native rest bounds155..474.
alpha=np.array(small[0])[:,:,3]>=128;yy,xx=np.where(alpha);rest_height=int(yy.max()-yy.min()+1);scale=399/rest_height;dx=16.25;dy=493-int(yy.max())*scale
keys=[]
for i,im in enumerate(small):
 full=im.transform((512,576),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BICUBIC);(out/'keys').mkdir(exist_ok=True);
 if i==0:full=Image.open(root/'research/sprite-animation/core-family-v56/frames/idle/W/00.png').convert('RGBA')
 full.save(out/'keys'/f'{i:02}.png');keys.append(full)
sequence=list(range(8))+list(reversed(range(8)));(out/'frames').mkdir(exist_ok=True);records=[]
for n,k in enumerate(sequence):
 f=out/'frames'/f'{n:02}.png';keys[k].save(f);records.append({'path':str(f.relative_to(out)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'duration_ms':90 if n<15 else 550})
(out/'extraction.json').write_text(json.dumps({'keys':notes,'timeline_to_key':sequence,'new_unique_body_drawings':8,'timeline_exposures':16,'recovery_policy':'Reverse posed keys as explicit empty-hand recovery; no claim of16different drawings or independent cape/grasp recovery.','one_bank_matrix':[scale,0,0,scale,dx,dy],'neutral_calibration_only':True,'per_key_registration':False,'production_pass':False},indent=2)+'\n')
case=json.loads((root/'research/sprite-animation/pickup-views-v55/W-split-drape5-motion-case.json').read_text());case['frames']=[{k:f[k]for k in ['path','sha256']}for f in records];case['durations']=[f['duration_ms']for f in records];(out/'motion-case.json').write_text(json.dumps(case,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('motion',root/'tools/sprite-motion-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);motion=m.evaluate(case,out);(out/'motion-review.json').write_text(json.dumps(motion,indent=2)+'\n');print('motion',motion['motion_profile_pass'],motion.get('measurements'),motion.get('checks'))
clip={'title':'New whole-body W candidate /8 drawings16exposures /NOT APPROVED','canvas':[512,576],'frames':records};(out/'clip.json').write_text(json.dumps(clip,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('review',root/'tools/sprite-review-pack.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if not(out/'review').exists():m.build(out/'clip.json',out/'review')
print([(r['key'],r['native_bbox'])for r in notes])

contact={'frames':[{k:r[k]for k in ('path','sha256')}for r in records],'surfaces':{'visible_overlap_boot':{'window':[150,465,310,515],'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}}}}
(out/'contact-case.json').write_text(json.dumps(contact,indent=2))
spec=importlib.util.spec_from_file_location('contact',root/'tools/sprite-contact-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.evaluate(contact,out);(out/'contact-review.json').write_text(json.dumps(r,indent=2));print('CONTACT',r['visible_surface_contact_pass'],r['summary'])
