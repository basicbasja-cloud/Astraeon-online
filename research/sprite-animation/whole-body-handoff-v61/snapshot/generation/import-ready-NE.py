from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np,importlib.util
from scipy.ndimage import label,binary_dilation
root=Path.cwd();g=root/'work/all-actions-v61/generation';catalog=json.loads((root/'research/sprite-animation/core-family-v56/catalog.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name):
 spec=importlib.util.spec_from_file_location(name,root/f'tools/sprite-{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for v,filename in [('N','exec-f66e29ac-eb8b-45e9-89fe-1f2182b56975.png'),('E','exec-2f7cc4a7-2d00-4440-8778-e4b3343f14ba.png')]:
 out=g/f'{v}-ready-candidate1';out.mkdir(exist_ok=True);rawpath=Path('/workspace/generated_images')/filename;raw=Image.open(rawpath).convert('RGBA');assert raw.size==(1536,1024);small=[];frames=[];notes=[]
 for i in range(8):
  x=i%4*384;y=i//4*512;a=np.array(raw.crop((x,y,x+384,y+512)));allowed=np.zeros((512,384),bool);allowed[70:504,32:365]=True;core=(a[:,:,3]>=128)&allowed;lab,n=label(core);areas=np.bincount(lab.ravel());areas[0]=0;owner=int(np.argmax(areas));others=[int(n)for k,n in enumerate(areas)if k and k!=owner and n>=40];assert not others,(v,i,others)
  mask=binary_dilation(lab==owner,iterations=3)&allowed;b=a.copy();b[~mask]=0;assert np.array_equal(b[mask],a[mask]);im=Image.fromarray(b);(out/'native-keys').mkdir(exist_ok=True);im.save(out/'native-keys'/f'{i:02}.png')
  # Shared guide calibration .8seed x=-13 y80 =>inverse1.25 x16.25 y-100.
  im=im.transform((512,576),Image.Transform.AFFINE,(.8,0,-13,0,.8,80),Image.Resampling.BICUBIC);(out/'keys').mkdir(exist_ok=True);im.save(out/'keys'/f'{i:02}.png');small.append(im)
  yy,xx=np.where(np.array(im)[:,:,3]>=128);notes.append({'key':i,'source_cell':i,'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'native_sha256':sha(out/'native-keys'/f'{i:02}.png'),'output_sha256':sha(out/'keys'/f'{i:02}.png')})
 clip0=catalog['actions']['ready']['clips'][v];durations=clip0['durations_ms'];assert len(durations)==24;mapping=[i//3 for i in range(24)];(out/'frames').mkdir(exist_ok=True)
 for i,k in enumerate(mapping):
  f=out/'frames'/f'{i:02}.png';small[k].save(f);frames.append({'path':str(f.relative_to(out)),'sha256':sha(f),'duration_ms':durations[i]})
 clip={'title':f'{v} ready native8drawings/24timelineexposures /NOT APPROVED','canvas':[512,576],'frames':frames};(out/'clip.json').write_text(json.dumps(clip,indent=2));(out/'import.json').write_text(json.dumps({'source_sha256':sha(rawpath),'source':str(rawpath),'source_grid':[4,2],'annotation_rect':[32,70,365,504],'matte':'primaryopaquecomponentplus3pxenvelope,unmodifiedsourceRGBAinside','shared_authoring_matrix':[1.25,0,0,1.25,16.25,-100],'per_frame_registration':False,'keys':notes,'timeline_to_key':mapping,'unique_drawings':8,'timeline_exposures':24,'production_pass':False},indent=2))
 surfaces={'near_overlapped_boot':{'window':[150,465,310,515],'planted_frames':list(range(24)),'budget_px':{'x':6,'y':6}}}if v=='W'else {k:{'window':w,'planted_frames':list(range(24)),'budget_px':{'x':6,'y':6}}for k,w in [('screen_left',[150,450,255,520]),('screen_right',[270,450,355,520])]}
 
 if v=='E':surfaces={'near_overlapped_boot':{'window':[200,465,330,515],'planted_frames':list(range(24)),'budget_px':{'x':6,'y':6}}}
 if v=='N':surfaces={k:{'window':w,'planted_frames':list(range(24)),'budget_px':{'x':6,'y':6}}for k,w in [('screen_left',[180,450,265,520]),('screen_right',[270,450,335,520])]}
 case={'frames':[{k:r[k]for k in ['path','sha256']}for r in frames],'surfaces':surfaces};(out/'contact-case.json').write_text(json.dumps(case,indent=2));review=module('contact-review').evaluate(case,out);(out/'contact-review.json').write_text(json.dumps(review,indent=2));print(v,'solepass',review['visible_surface_contact_pass'],review['summary'],'crowns',[k['bbox'][1]for k in notes])
 if not(out/'review').exists():module('review-pack').build(out/'clip.json',out/'review')
