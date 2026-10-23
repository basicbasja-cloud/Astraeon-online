from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
s=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study/head-locked-prefix-study')
raw=s/'raw-repaint.png'
a=Image.open(raw).convert('RGB');ref=Image.open(s/'input-2x2-plate.png').convert('RGB');frames=[];rows=[];report=[]
def bounds(im):
 x=np.array(im);mask=(x.min(2)<180)&(x.max(2)-x.min(2)>15);ys,xs=np.where(mask);return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
for i in range(4):
 x=i%2;y=i//2
 f=a.crop((x*a.width//2,y*a.height//2,(x+1)*a.width//2,(y+1)*a.height//2)).resize((768,768),Image.Resampling.LANCZOS)
 r=ref.crop((x*768,y*768,(x+1)*768,(y+1)*768));f.save(s/f'candidate-{i:03}.png');frames.append(f.resize((240,240),Image.Resampling.LANCZOS))
 b=bounds(f);c=bounds(r);report.append({'frame':i,'candidate_color_bounds':b,'reference_color_bounds':c,'height_ratio':(b[3]-b[1])/(c[3]-c[1]),'top_displacement_px':b[1]-c[1]})
 row=Image.new('RGB',(768,384),'white');row.paste(r.resize((384,384)),(0,0));row.paste(f.resize((384,384)),(384,0));rows.append(row)
contact=Image.new('RGB',(768,1536),'white')
for i,r in enumerate(rows):contact.paste(r,(0,i*384))
contact.save(s/'source-vs-candidate.png')
for speed,ms in [('normal',60),('slow',240)]:frames[0].save(s/f'prefix-{speed}.gif',save_all=True,append_images=frames[1:],duration=ms,loop=0)
result={'status':'REJECTED_FIXED_CAMERA_LAYOUT_DRIFT','method':'Uniform 2x2 slicing and uniform canvas resizing only. Color bounds are diagnostic, never used to fit artwork.','raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'frames':report,'runtime_admitted':False,'reason':'Generated actors expand vertically and lose the fixed source framing. Do not repair with per-frame bounding-box fitting.'}
(s/'layout-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
