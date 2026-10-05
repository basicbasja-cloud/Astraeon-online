"""Original shared prop-surface artwork; retains each native city's material hue."""
import json,hashlib,random,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];r=random.Random(6945);rng=np.random.default_rng(6945);n=1024;yy,xx=np.mgrid[:n,:n];records={}
def save(name,field,size,detail):
 a=np.clip(field,0,255).astype('uint8');im=Image.fromarray(np.stack([a,a,a],axis=2));master=ROOT/'authoring/materials'/(name+'-source.png');asset=ROOT/'assets'/(name+'.webp');im.save(master);im.save(asset,lossless=True,method=6);v=np.asarray(im,dtype=float)/255;linear=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
 records[name]={'size':[n,n],'master':master.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'texture':{'file':asset.relative_to(ROOT).as_posix(),'grid':[1,1],'tile':0,'worldSize':size,'paletteDetail':detail,'meanLinearRGB':linear.mean(axis=(0,1)).round(7).tolist(),'anisotropy':4}}
noise=rng.normal(0,2,(n,n));broad=5*np.sin(xx*math.tau/n*3+2*np.sin(yy*math.tau/n*2))+3*np.sin(yy*math.tau/n*5)
metal=170+broad+noise+2*np.sin(xx*math.tau/n*190)
for _ in range(300):
 x,y=r.randrange(n),r.randrange(n);radius=r.randrange(1,4);metal[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1]-=r.randrange(8,19)
for _ in range(65):
 x,y=r.randrange(n-100),r.randrange(n);length=r.randrange(20,90);metal[y:y+1,x:x+length]+=r.randrange(5,12)
save('wayfarer-prop-metal-v69',metal,1.4,.50)
cloth=174+broad+noise+3*np.sin(xx*math.tau/n*128)+3*np.sin(yy*math.tau/n*128)+6*np.sin(xx*math.tau/n*2+np.sin(yy*math.tau/n))
save('wayfarer-prop-cloth-v69',cloth,1.1,.52)
petal=184+noise+4*np.sin(xx*math.tau/n*13+np.sin(yy*math.tau/n*3))+6*np.sin(yy*math.tau/n*2)
save('wayfarer-prop-petal-v69',petal,.8,.45)
rind=174+broad*.4+rng.normal(0,3.4,(n,n))+2*np.sin(xx*math.tau/n*72)*np.sin(yy*math.tau/n*68)
save('wayfarer-prop-rind-v69',rind,.9,.45)
paper=184+broad+noise+3*np.sin(xx*math.tau/n*38)*np.sin(yy*math.tau/n*27)
save('wayfarer-prop-paper-v69',paper,1.5,.50)
(ROOT/'authoring/materials/wayfarer-prop-detail-v69.json').write_text(json.dumps({'sourcePass':69,'origin':'Original seeded subtle metal wear, textile weave, petal veins, produce rind and paper fiber; no reference pixels imported','colorPolicy':'Neutral measured textures preserve the native material palette and geometry lighting','materials':records},indent=2)+'\n');print('PASS five original1024² editable lossless prop surfaces')
