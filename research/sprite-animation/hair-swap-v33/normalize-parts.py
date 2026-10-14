"""Crop actual generated complete components without painting retained pixels.
Refuse a major component crossing an atlas panel. Keep rejected raw packing.
"""
from pathlib import Path
import hashlib,json
import cv2,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];out=P/'parts';out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
rows=[]
for name,file,box in [('head.base','head-raw.png',[0,0,1254,1254]),('silver.rear','hair-atlas-repaired-raw.png',[0,0,627,627]),('silver.front','hair-atlas-repaired-raw.png',[627,0,1254,627]),('auburn.rear','hair-atlas-repaired-raw.png',[0,627,627,1254]),('auburn.front','hair-atlas-repaired-raw.png',[627,627,1254,1254])]:
 a=np.array(Image.open(P/file).convert('RGBA'));n,l,stats,_=cv2.connectedComponentsWithStats((a[:,:,3]>0).astype('uint8'),8)
 candidates=[(int(r[4]),i) for i,r in enumerate(stats) if i and r[4]>5000 and box[0]<=r[0]+r[2]/2<box[2] and box[1]<=r[1]+r[3]/2<box[3]]
 if len(candidates)!=1:raise ValueError('Unknown/touching component packing: '+name)
 _,i=candidates[0];x,y,w,h,area=stats[i]
 if x<=box[0] or y<=box[1] or x+w>=box[2] or y+h>=box[3]:raise ValueError('Component crosses crop/gutter: '+name)
 b=a[box[1]:box[3],box[0]:box[2]].copy();keep=l[box[1]:box[3],box[0]:box[2]]==i;discard=int(((b[:,:,3]>0)&~keep).sum());b[~keep]=0
 path=out/(name+'.png');Image.fromarray(b).save(path)
 rows.append({'name':name,'path':rel(path),'sha256':sha(path),'raw_file':rel(P/file),'raw_sha256':sha(P/file),'raw_box':box,'retained_RGBA_unchanged':True,'removed_detached_alpha_pixels':discard,'complete_component_box':[int(v) for v in [x,y,w,h]],'semantic_role':'complete bald head/ears/neck' if name=='head.base' else 'hair only, '+name.split('.')[1]+' depth layer','mirrored':False})
(P/'parts.json').write_text(json.dumps({'parts':rows,'scope':'One fixed camera; one complete generated bald head plus two genuine front/rear hair pairs.'},indent=2)+'\n');print('COMPLETE_PARTS',len(rows))
