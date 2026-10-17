from pathlib import Path
from PIL import Image
from scipy.ndimage import label,binary_dilation
import numpy as np,json,hashlib,importlib.util
root=Path.cwd();g=root/'work/all-actions-v61/generation';catalog=json.loads((root/'research/sprite-animation/core-family-v56/catalog.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(name):
 spec=importlib.util.spec_from_file_location(name,root/f'tools/sprite-{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for v in ['S','W']:
 out=g/f'{v}-walk-candidate1';out.mkdir(exist_ok=True);small=[];notes=[]
 if v=='S':
  raw=Image.open('/workspace/generated_images/exec-413a7a1a-38e5-4e28-b317-f385ea6238db.png').convert('RGBA');fix=Image.open('/workspace/generated_images/exec-20c319d3-d046-4f65-874d-678f5850c62c.png').convert('RGBA');assert fix.size==(1536,1024);fix=fix.resize((768,512),Image.Resampling.LANCZOS)
 for i in range(8):
  if v=='W':im=Image.open(out/'native-even'/f'{i:02}.png').convert('RGBA');source='selected originalRO/armfix native cell';rect=[80,130,335,500]
  elif i in [5,6]:im=fix.crop(((i-5)*384,0,(i-4)*384,512));source='targeted native wholepose leftstep redraw';rect=[80,100,335,504]
  else:x=i%4*384;y=i//4*512;im=raw.crop((x,y,x+384,y+512));source='original new native cell';rect=[80,100,335,504]
  a=np.array(im);allowed=np.zeros((512,384),bool);allowed[rect[1]:rect[3],rect[0]:rect[2]]=True;lab,n=label((a[:,:,3]>=128)&allowed);areas=np.bincount(lab.ravel());areas[0]=0;owner=int(np.argmax(areas));others=[int(n)for j,n in enumerate(areas)if j and j!=owner and n>=40];assert not others,(v,i,others);keep=binary_dilation(lab==owner,iterations=3)&allowed;a[~keep]=0;im=Image.fromarray(a);(out/'native-keys').mkdir(exist_ok=True);im.save(out/'native-keys'/f'{i:02}.png');small.append(im);yy,xx=np.where(a[:,:,3]>=128);notes.append({'key':i,'source':source,'fixed_annotation_rect':rect,'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'native_sha256':sha(out/'native-keys'/f'{i:02}.png')})
 if v=='S':
  # Frame0 is an upright neutral crossing/rest drawing, both knees straight,
  # arms hanging. One family adapter only. All8 keys use identical matrix.
  y0=notes[0]['bbox'][1];y1=notes[0]['bbox'][3]-1;scale=399/(y1-y0+1);dx=255-191*scale;dy=493-y1*scale;calibration='one upright neutral pose0 height and manually authored neutral head center191 -> original255; no perpose registration'
 else:scale=1.25;dx=16.25;dy=-100;calibration='inverse of original shared .8neutral-guide display; no pose fitting'
 frames=[];crown=[];centers=[];(out/'keys').mkdir(exist_ok=True)
 for i,im in enumerate(small):
  full=im.transform((512,576),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BICUBIC);full.save(out/'keys'/f'{i:02}.png');a=np.array(full)[:,:,3]>=128;yy,xx=np.where(a);top=int(yy.min());near=np.where(a[top:top+12]);crown.append(top);centers.append(float(np.mean(near[1])))
 durations=catalog['actions']['walk']['clips'][v]['durations_ms'];assert len(durations)==80;(out/'frames').mkdir(exist_ok=True)
 for i in range(80):k=i//10;f=out/'frames'/f'{i:02}.png';Image.open(out/'keys'/f'{k:02}.png').save(f);frames.append({'path':str(f.relative_to(out)),'sha256':sha(f),'duration_ms':durations[i]})
 clip={'title':f'{v} native fullbody walk8drawings/80clockexposures NOT APPROVED','canvas':[512,576],'frames':frames};(out/'clip.json').write_text(json.dumps(clip,indent=2));step=max(abs(crown[(i+1)%8]-crown[i])for i in range(8));xstep=max(abs(centers[(i+1)%8]-centers[i])for i in range(8));r={'visible_crown_range_px':max(crown)-min(crown),'visible_crown_max_step_px':step,'top_band_x_mean_max_step_px':xstep,'crowns':crown,'topband_xmeans':centers,'budgets':{'max_vertical_step_px':3,'max_vertical_range_px':6,'max_horizontal_step_px':3},'visible_crown_profile_pass':step<=3 and max(crown)-min(crown)<=6 and xstep<=3,'production_pass':False,'scope':'Crown-only visible bob; not an anatomical root/contact/leg ownership detector'};(out/'crown-review.json').write_text(json.dumps(r,indent=2));(out/'import.json').write_text(json.dumps({'keys':notes,'common_bank_matrix':[scale,0,0,scale,dx,dy],'calibration':calibration,'per_frame_registration':False,'new_native_drawings':8,'timeline_exposures':80,'durations_ms':durations,'production_pass':False},indent=2));print(v,r)
 if not(out/'review').exists():mod('review-pack').build(out/'clip.json',out/'review')
