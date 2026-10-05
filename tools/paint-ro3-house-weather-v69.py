"""Original aged limewash and damp masonry detail; no reference pixels used."""
import hashlib,json,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
r=random.Random(6945);n=1024
# Periodic coarse and fine fields avoid visible seams or a uniform clean face.
def field(size):
 a=np.array([[r.randrange(256) for _ in range(size)] for _ in range(size)],dtype=np.uint8)
 expanded=np.tile(a,(3,3))
 return np.asarray(Image.fromarray(expanded).resize((n*3,n*3),Image.Resampling.BICUBIC),dtype=float)[n:n*2,n:n*2]/255-.5
noise=field(12)*28+field(38)*11+field(160)*5
base=np.stack([222+noise,210+noise,184+noise],axis=2).clip(0,255).astype('uint8')
im=Image.fromarray(base);d=ImageDraw.Draw(im)
for j in range(170):
 x,y=r.randrange(n),r.randrange(n);c=(185,174,152)
 # Thin short plaster checking and scattered exposed aggregate, not black webs.
 if j%6==0:
  pts=[(x,y)]
  for _ in range(r.randrange(2,6)):
   x+=r.randrange(-9,10);y+=r.randrange(4,12);pts.append((x,y))
  d.line(pts,fill=c,width=1)
 else:d.ellipse((x,y,x+r.randrange(1,4),y+r.randrange(1,3)),fill=(202,190,165))
# Transparent, broken vertical base patina. Native UV maps its full height
# only onto the bottom of a wall, never repeats it through upper storeys.
f=field(24);a=np.zeros((n,n,4),dtype=np.uint8)
for y in range(n):
 strength=(1-y/(n-1))**2
 a[y,:,0]=95;a[y,:,1]=96;a[y,:,2]=62
 a[y,:,3]=np.clip((strength*(.6+f[y]*1.1))*115,0,125).astype('uint8')
patina=Image.fromarray(a)
out={}
for suffix,pic,size,detail in [('limewash',im,3.2,.80),('patina',patina,2.4,.68)]:
 name='wayfarer-'+suffix+'-v69';master=ROOT/'authoring/materials'/f'{name}-source.png';asset=ROOT/'assets'/f'{name}.webp'
 pic.save(master);pic.save(asset,lossless=True,method=6)
 rgb=np.asarray(pic.convert('RGB'),dtype=float)/255;lin=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 spec={'file':asset.relative_to(ROOT).as_posix(),'grid':[1,1],'tile':0,'worldSize':size,'meanLinearRGB':lin.mean((0,1)).round(7).tolist(),'paletteDetail':detail}
 if suffix=='patina':spec.update(alphaCutoff=.01,alphaBlend=True)
 out[suffix]={'texture':spec,'master':master.relative_to(ROOT).as_posix(),'size':list(pic.size),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()}
(ROOT/'authoring/materials/wayfarer-house-weather-v69.json').write_text(json.dumps({'sourcePass':69,'reference':'RO3 04_08_45/39: mottled limewash, worn foundation masonry','referencePixelsUsed':False,'materials':out},indent=2)+'\n')
print('Authored original weathered limewash and foundation patina')
