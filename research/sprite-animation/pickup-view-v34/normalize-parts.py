"""Explicit inspected atlas panels. Retain source RGBA; never fit motion frames."""
from pathlib import Path
import hashlib,json
import cv2,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
specs=[
 ('head_hair',[0,0,371,378],[182,325],None,.52),
 ('torso',[371,0,639,378],[139,100],[156,313],.50),
 ('teal_panel',[1018,0,1254,378],[108,135],None,.33),
 ('left.upperarm',[0,378,318,646],[184,64],[120,204],.22),
 ('left.forearm',[318,378,637,646],[142,64],[218,206],.22),
 ('right.upperarm',[637,378,952,646],[140,61],[220,201],.24),
 ('right.forearm',[952,378,1254,655],[139,63],[203,209],.24),
 ('left.thigh',[0,646,318,942],[186,34],[163,229],.31),
 ('left.shin',[318,640,637,942],[176,56],[170,246],.28),
 ('right.thigh',[637,646,952,942],[173,34],[188,229],.33),
 ('right.shin',[952,640,1254,955],[172,56],[174,246],.31),
 ('left.foot',[0,942,350,1254],[167,107],None,.29),
 ('right.foot',[350,942,683,1254],[154,107],None,.30),
 ('front_tabard',[683,942,952,1254],[147,36],None,.39),
 ('side_tabard',[952,942,1254,1254],[167,48],None,.37)]
extra=[
 ('head.base',[0,0,590,630],[322,565],None,.34),
 ('hair.front',[590,0,1254,630],[247,565],None,.34),
 ('hair.rear',[0,630,628,1254],[310,565],None,.31),
 ('cape',[627,630,1254,1254],[464,120],None,.32)]
specs=[s for s in specs if s[0] not in ('left.thigh','right.thigh','front_tabard','side_tabard')]
extra=[s for s in extra if not s[0].startswith('hair.')]
hair=[('hair.front',[0,0,1100,793],[535,915],None,.20),('hair.rear',[1100,0,1983,793],[440,789],None,.24)]
repair=[('left.thigh',[0,0,627,627],[350,195],[348,510],.22),('right.thigh',[627,0,1254,627],[304,190],[326,505],.24),('front_tabard',[0,627,627,1254],[357,121],None,.27),('side_tabard',[627,627,1254,1254],[313,133],None,.23)]
repair=[s for s in repair if s[0] not in ('left.thigh','right.thigh')]
closed=[('left.thigh',[0,0,887,887],[460,170],[474,785],.12),('right.thigh',[887,0,1774,887],[425,180],[533,785],.12)]
(P/'parts').mkdir(exist_ok=True);rows=[];receipts=[]
for rawfile,spec in [('atlas-raw.png',s) for s in specs]+[('head-cape-raw.png',s) for s in extra]+[('packing-repair-raw.png',s) for s in repair]+[('hair-fit-raw.png',s) for s in hair]+[('closed-thigh-raw.png',s) for s in closed]:
 name,box,pivot,end,width=spec;raw=P/rawfile;crop=np.array(Image.open(raw).convert('RGBA').crop(box));n,labels,stats,_=cv2.connectedComponentsWithStats((crop[:,:,3]>0).astype('uint8'),8)
 assert n>1;chosen=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));keep=labels==chosen
 discarded=int(((crop[:,:,3]>0)&~keep).sum());crop[~keep]=0
 # Reject packing failures that would require cutting the substantial asset.
 y,x=np.where(keep);assert min(x)>0 and max(x)<crop.shape[1]-1 and min(y)>0 and max(y)<crop.shape[0]-1,(name,'component crosses panel')
 file=P/'parts'/(name+'.png');Image.fromarray(crop).save(file)
 rows.append(dict(name=name,file=str(file.relative_to(ROOT)),sha256=sha(file),pivot=pivot,end=end,width_scale=width,semantic_owner=name.split('.')[0] if name.startswith(('left.','right.')) else 'body',view='B',mirrored=False,source_atlas=str(raw.relative_to(ROOT)),atlas_box=box,raw_sha256=sha(raw),retained_RGBA_unchanged=True))
 receipts.append(dict(name=name,discarded_detached_pixels=discarded,retained_RGBA_unchanged=True,component_bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]))
(P/'parts.json').write_text(json.dumps(dict(view='B',parts=rows,scope='19 assets:16 active original,18 active silver,16 bald; physical opposite view only'),indent=2)+'\n')
(P/'normalization-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('NORMALIZED',len(rows))
