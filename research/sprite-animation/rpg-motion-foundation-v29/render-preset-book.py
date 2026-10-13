#!/usr/bin/env python3
"""Original diagnostic drawings from actual external source samples.
Common projection/range per rig bank; no per-pose recenter, mirroring or fitting.
"""
import gzip,hashlib,json,math,re
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
report=json.loads(gzip.decompress((ROOT/'preset-samples.json.gz').read_bytes()))
out=ROOT/'preset-boards';out.mkdir(exist_ok=True);boards=[]
def project(p):
 x,y,z=p;return (0.866*x+0.5*y,-z+0.22*(-0.5*x+0.866*y))
for f in report['files']:
 points=[project(p) for clip in f['clips'] for s in clip['samples'] for p in s['world_joints'].values()]
 xmin=min(p[0] for p in points);xmax=max(p[0] for p in points);ymin=min(p[1] for p in points);ymax=max(p[1] for p in points)
 scale=min(165/max(xmax-xmin,1e-8),180/max(ymax-ymin,1e-8));ox=100-scale*(xmin+xmax)/2;oy=42-scale*ymin
 for clip in f['clips']:
  im=Image.new('RGB',(200*len(clip['samples']),250),(29,33,41));draw=ImageDraw.Draw(im)
  for i,s in enumerate(clip['samples']):
   draw.text((i*200+8,6),clip['name'][:25],fill='white');draw.text((i*200+8,23),f"key {s['native_key_index']} / {s['source_time_seconds']:.3f}s",fill='#c6c6cc')
   for n,b in f['bones'].items():
    if b['parent'] not in s['world_joints']:continue
    p=project(s['world_joints'][n]);q=project(s['world_joints'][b['parent']])
    side='right' if n.endswith('_r') or 'right' in n.lower() else ('left' if n.endswith('_l') or 'left' in n.lower() else 'center')
    color={'right':(50,155,255),'left':(255,151,42),'center':(205,215,222)}[side]
    a=(round(i*200+ox+scale*p[0]),round(oy+scale*p[1]));b=(round(i*200+ox+scale*q[0]),round(oy+scale*q[1]));draw.line((a,b),fill=color,width=2);draw.ellipse((a[0]-2,a[1]-2,a[0]+2,a[1]+2),fill=color)
   draw.text((i*200+8,228),'Source only; contact unknown',fill='#999fa8')
  filename=f['source_id']+'--'+re.sub('[^a-zA-Z0-9_-]','_',clip['name'])+'.png';im.save(out/filename)
  boards.append({'source_id':f['source_id'],'clip':clip['name'],'file':'preset-boards/'+filename,'sha256':hashlib.sha256((out/filename).read_bytes()).hexdigest(),'samples':len(clip['samples']),'projection':{'x':'0.866*x+0.5*y','y':'-z+0.22*(-0.5*x+0.866*y)','scale':scale,'offset':[ox,oy]},'anatomical_color_source':'Serialized source bone names; no image leg identity detection','contacts':'unknown','production_pass':False})
(ROOT/'preset-board-manifest.json').write_text(json.dumps({'boards':boards},indent=2)+'\n')
print(json.dumps({'boards':len(boards),'actual_source_sampled_poses':sum(b['samples'] for b in boards)}))
