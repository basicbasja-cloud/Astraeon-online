"""Review actual old/new captures with identical bank transform and shared ROIs."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;OLD=P.parent/'free-character-v44';views=['S','SE','E','NE','N','NW','W','SW'];BG=(36,40,47,255);before=json.loads((OLD/'receipt.json').read_text());after=json.loads((P/'receipt.json').read_text());ims=[]
for i in range(27):
 out=Image.new('RGBA',(1536,512),BG);d=ImageDraw.Draw(out)
 for j,v in enumerate(views):
  x=j%4*384;y=j//4*256
  # Each unchanged full canvas is reduced uniformly by1/2, no body/arm fitting.
  for k,root in enumerate([OLD,P]):
   im=Image.open(root/f'review/dense/{v}/{i:02}.png').resize((192,256),Image.Resampling.LANCZOS);out.alpha_composite(im,(x+k*192,y));d.text((x+k*192+8,y+8),v+(' BEFORE' if k==0 else ' AFTER'),fill='white')
 ims.append(out.resize((1152,384),Image.Resampling.LANCZOS).convert('RGB'))
ims[0].save(P/'before-after-eight.gif',save_all=True,append_images=ims[1:],duration=[50]*26+[600],loop=0,disposal=2)
# Same raw-image crop for all keys and both variants in a view, derived from
# the union of declared source joint projections plus fixed32px margin.
plate=Image.new('RGBA',(960,2048),BG);d=ImageDraw.Draw(plate);rois={}
for row,v in enumerate(views):
 pts=[f['projected_points'][v]['left.'+k] for r in [before,after] for f in r['frames'] for k in ['shoulder','elbow','wrist','palm','grip']];x0=max(0,int(min(p[0] for p in pts))-32);x1=min(384,int(max(p[0] for p in pts))+33);y0=max(0,int(min(p[1] for p in pts))-32);y1=min(512,int(max(p[1] for p in pts))+33);roi=[x0,y0,x1,y1];rois[v]=roi;scale=min(220/(x1-x0),230/(y1-y0));size=(round((x1-x0)*scale),round((y1-y0)*scale))
 for col,(root,index,label) in enumerate([(OLD,0,'BEFORE REST'),(P,0,'AFTER REST'),(OLD,3,'BEFORE BEND'),(P,3,'AFTER BEND')]):
  im=Image.open(root/f'renders/key/{v}/{index:02}.png').crop(roi).resize(size,Image.Resampling.LANCZOS);plate.alpha_composite(im,(col*240+(240-size[0])//2,row*256+22));d.text((col*240+7,row*256+4),v+' '+label,fill='white')
plate.save(P/'left-arm-before-after.png');(P/'comparison-layout.json').write_text(json.dumps(dict(crop_boxes=rois,rule='One union-of-source-projections ROI per view shared unchanged across before/after and all phases. Uniform review reduction only; not image anatomy tracking, individual feature fit or sprite repair.',production_pass=False),indent=2)+'\n')
# Actual full-scene left surface passes; occluded arm pixels remain occluded.
mat=json.loads((P/'display-bind.json').read_text())['matrix'];s,tx,ty=mat[0],mat[4],mat[5];inv=(1/s,0,-tx/s,0,1/s,-ty/s);ims=[]
for i in range(8):
 out=Image.new('RGBA',(768,512),BG);d=ImageDraw.Draw(out)
 for j,v in enumerate(views):
  src=Image.open(P/f'arm-visibility/depth_tested/{v}/{i:02}.png').transform((384,512),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC).resize((192,256),Image.Resampling.LANCZOS);out.alpha_composite(src,(j%4*192,j//4*256));d.text((j%4*192+5,j//4*256+5),v+' LEFT / '+str(i+1),fill='white')
 ims.append(out.convert('RGB'))
ims[0].save(P/'left-surface-eight.gif',save_all=True,append_images=ims[1:],duration=[190,180,190,180,190,180,190,600],loop=0,disposal=2);print('Actual comparisons built')
