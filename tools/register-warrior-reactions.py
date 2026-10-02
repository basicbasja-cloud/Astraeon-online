"""Register connected authored sprites; source artwork is never repainted. Requires scipy, numpy, Pillow."""
from pathlib import Path
import json,shutil,sys
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[1];src=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'authoring/characters/warrior-reactions-v3.png'
out=ROOT/'authoring/characters';out.mkdir(exist_ok=True);
if src.resolve()!=(out/'warrior-reactions-v3.png').resolve():shutil.copyfile(src,out/'warrior-reactions-v3.png')
im=Image.open(src).convert('RGBA');im.save(ROOT/'assets/warrior-reactions-v3.webp',quality=94,method=6)
a=np.asarray(im)[:,:,3];labels,count=ndimage.label(a>128);components=[]
for k in range(1,count+1):
 ys,xs=np.nonzero(labels==k)
 if len(xs)<800:continue
 row=int(ys.min()//(im.height/4));col=int(xs.mean()//(im.width/4));components.append((row*4+col,k))
assert len(components)==16 and len(set(i for i,k in components))==16
frames=[]
def simplify(points,eps=1.25):
 if len(points)<3:return points
 p=np.array(points,dtype=float);v=p[-1]-p[0];norm=np.linalg.norm(v);d=np.linalg.norm(p-p[0],axis=1) if norm==0 else np.abs(v[0]*(p[:,1]-p[0,1])-v[1]*(p[:,0]-p[0,0]))/norm;j=int(d.argmax())
 return simplify(points[:j+1],eps)[:-1]+simplify(points[j:],eps) if d[j]>eps else [points[0],points[-1]]
for i,k in sorted(components):
 mask=ndimage.binary_fill_holes(ndimage.binary_dilation(labels==k,iterations=2));ys,xs=np.nonzero(mask);x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
 m=mask[y0:y1,x0:x1];edges={}
 # Directed pixel-boundary contour; excludes artwork belonging to neighbouring cells.
 for y,x in zip(*np.nonzero(m)):
  if y==0 or not m[y-1,x]:edges[(x,y)]=(x+1,y)
  if x==m.shape[1]-1 or not m[y,x+1]:edges[(x+1,y)]=(x+1,y+1)
  if y==m.shape[0]-1 or not m[y+1,x]:edges[(x+1,y+1)]=(x,y+1)
  if x==0 or not m[y,x-1]:edges[(x,y+1)]=(x,y)
 loops=[]
 while edges:
  start=next(iter(edges));p=start;loop=[]
  while p in edges:loop.append(p);p=edges.pop(p)
  if p==start:loops.append(loop)
 contour=max(loops,key=len);half=len(contour)//2;outline=simplify(contour[:half+1])+simplify(contour[half:]+[contour[0]])[1:-1]
 ay=y1-y0;bottom=np.nonzero((labels[y0:y1,x0:x1]==k)&(np.indices(m.shape)[0]>=ay-10))[1];ax=([170,805,180,780,184,753,183,827][i//2]-x0) if i%2==0 else (x1-x0)/2
 frames.append({'direction':['S','SE','E','NE','N','NW','W','SW'][i//2],'state':'hit' if i%2==0 else 'death','rect':[x0,y0,x1-x0,y1-y0],'anchor':[round(ax,2),ay],'outline':outline,'standingHeight':y1-y0 if i%2==0 else frames[-1]['standingHeight']})
manifest=ROOT/'world/v3/warrior-animation.json';data=json.loads(manifest.read_text());data['reactions']={'atlas':'assets/warrior-reactions-v3.webp','clip':'warrior-reactions-v3','cols':2,'rows':8,'frames':frames};manifest.write_text(json.dumps(data,indent=2,default=int)+'\n')
print([(f['direction'],f['state'],f['rect'],f['anchor'],len(f['outline'])) for f in frames])
